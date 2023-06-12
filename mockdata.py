from calendar import monthrange
from random import randint

import taos


def create_db(conn, db_name):
    print("Creating database ...")
    conn.execute(f"DROP DATABASE IF EXISTS {db_name}")
    conn.execute(f"CREATE DATABASE {db_name}")


def create_table(conn, db_name, table_name):
    print("Creating table ...")
    conn.execute(f"CREATE TABLE {db_name}.{table_name} (ts TIMESTAMP, num INT)")


def insert_rec_per_month(conn, db_name, table_name, year, month):
    print("Inserting data ...")
    increment = (year - 2014) * 1.1
    base = int(10 * increment)
    if month < 10 and month > 5:
        factor = 10
    else:
        factor = 8
    for day in range(1, monthrange(year, month)[1] + 1):
        num = base * randint(5, factor) + randint(0, factor)
        sql = f"INSERT INTO {db_name}.{table_name} VALUES ('{year}-{month}-{day} 00:00:00.000', {num})"
        try:
            conn.execute(sql)
        except Exception as e:
            print(f"command: {sql}")
            print(e)
            exit(1)


def insert_rec(conn, db_name, table_name):
    for year in range(2015, 2023):
        for month in range(1, 13):
            insert_rec_per_month(conn, db_name, table_name, year, month)


if __name__ == "__main__":
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

    create_db(conn, "power")
    create_table(conn, "power", "meters")
    insert_rec(conn, "power", "meters")

    conn.close()

    print("\nDone to mock data!")
