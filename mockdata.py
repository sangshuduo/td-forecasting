import argparse
from calendar import monthrange
from random import randint

import taos


def create_db(conn, db_name: str):
    print("Creating database ...")
    conn.execute(f"DROP DATABASE IF EXISTS {db_name}")
    conn.execute(f"CREATE DATABASE {db_name}")


def create_stable(conn, db_name: str, stable_name: str):
    print("Creating stable ...")
    conn.execute(
        f"CREATE STABLE {db_name}.{stable_name} (ts TIMESTAMP, num INT, temperature FLOAT) TAGS(device nchar(20))"
    )


def create_table(conn, db_name: str, stable_name: str, total: int):
    print("Creating table ...")
    for i in range(total):
        group_id = i % 10
        conn.execute(
            f"CREATE TABLE {db_name}.dev_{i} USING {db_name}.{stable_name} TAGS('dev_{group_id}')"
        )


def insert_rec_per_month(conn, db_name: str, device_seq: int, year: int, month: int):
    print(f"Inserting data for {year}-{month} to dev_{device_seq} ...")
    temp_inc = 1.01 ** (year - 2014)  # world become warmer year by year
    increment = (year - 2014) * 1.1
    base = int(10 * increment)
    if month < 10 and month > 5:
        factor = 9
    else:
        factor = 8
    for day in range(1, monthrange(year, month)[1] + 1):
        temperature = int(
            randint(0, (month if month < 10 else month - 9))
            + 3 * randint(8, factor) * temp_inc
        )

        extra_num = (temperature - 30) if temperature > 30 else 0
        num = base * randint(5, factor) + randint(0, factor) + extra_num
        sql = (
            f"INSERT INTO {db_name}.dev_{device_seq} VALUES "
            f"('{year}-{month}-{day} 00:00:00.000', {num}, {temperature})"
        )
        try:
            conn.execute(sql)
        except Exception as e:
            print(f"command: {sql}")
            print(e)
            exit(1)


def insert_rec(conn, db_name: str, device_seq: str):
    for year in range(2015, 2023):
        for month in range(1, 13):
            insert_rec_per_month(conn, db_name, device_seq, year, month)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="mockdata.py", description="Mock data for forecasting"
    )
    parser.add_argument(
        "--devices", type=int, help="specify the number of devices", required=False
    )

    args = parser.parse_args()

    try:
        conn = taos.connect(host="127.0.0.1")
    except Exception as e:
        print(e)
        exit(1)

    if conn is not None:
        print("Connected to TDengine!")
    else:
        print("Failed to connect to TDengine")
        exit(1)

    server_ver = conn.server_info
    print("server ver:", server_ver)

    if isinstance(args.devices, int) and args.devices > 0:
        TOTAL_DEVICE = args.devices
    else:
        TOTAL_DEVICE = 10
    create_db(conn, "power")
    create_stable(conn, "power", "meters")
    create_table(conn, "power", "meters", TOTAL_DEVICE)
    for i in range(TOTAL_DEVICE):
        insert_rec(conn, "power", i)

    conn.close()

    print("\nDone to mock data!")
