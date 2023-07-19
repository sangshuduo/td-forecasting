import argparse
from calendar import monthrange
from random import randint

import taos


def create_db(conn, db_name: str):
    print("Creating database ...")
    try:
        conn.execute(f"DROP DATABASE IF EXISTS {db_name}")
        conn.execute(f"CREATE DATABASE {db_name}")
    except Exception as e:
        print(e)
        exit(1)


def create_stable(conn, db_name: str, stable_name: str):
    print("Creating stable ...")
    try:
        conn.execute(
            f"CREATE STABLE {db_name}.{stable_name} (ts TIMESTAMP, num INT, temperature FLOAT, goods INT) TAGS(device nchar(20))"
        )
    except Exception as e:
        print(e)
        exit(1)


def create_table(conn, db_name: str, stable_name: str, total: int):
    print("Creating table ...")
    for i in range(total):
        group_id = i % 10
        try:
            conn.execute(
                f"CREATE TABLE {db_name}.dev_{i} USING {db_name}.{stable_name} TAGS('dev_{group_id}')"
            )
        except Exception as e:
            print(e)
            exit(1)


def insert_rec_per_month(conn, db_name: str, device_seq: int, year: int, month: int):
    print(f"Inserting data for {year}-{month} to dev_{device_seq} ...")
    inc_yoy = 1.05 ** (year - 2014)  # world become warmer year by year
    increment = int(
        ((year - 2014) * 12 + month - 1) * inc_yoy
    )  # connect to power consumption increase month by month
    for day in range(1, monthrange(year, month)[1] + 1):
        if month > 2 and month < 9:
            # temperature increase from Mar to Sep
            temperature = inc_yoy * randint(0 + month * 3, 10 + month * 3)
        else:
            # temperature decrease from Sep to Feb
            base_month = month + 12 if month < 3 else month
            temperature = inc_yoy * randint(
                0 + (17 - base_month) * 3, 10 + (17 - base_month) * 3
            )

        # for aircondition consume
        if day < 15:
            goods = randint(0, int(increment))
        else:
            goods = randint(int(increment * 0.5), int(1.5 * increment))
        extra_num = int(3 * (temperature - 25) if temperature > 25 else 0)
        num = increment * randint(5, 10) + goods + extra_num
        sql = (
            f"INSERT INTO {db_name}.dev_{device_seq} VALUES "
            f"('{year}-{month}-{day} 00:00:00.000', {num}, {temperature}, {goods})"
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
