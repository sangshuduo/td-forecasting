import argparse

import lightgbm as lgb
import matplotlib.pyplot as plt
import mlforecast
import pandas as pd
from mlforecast.target_transforms import Differences
from sklearn.linear_model import LinearRegression
from sqlalchemy import create_engine, text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="forecast.py", description="Forecast power consumption program"
    )
    parser.add_argument(
        "--dump", type=str, help="dump forecast picture to file", required=False
    )

    args = parser.parse_args()

    engine = create_engine("taos://root:taosdata@localhost:6030/power")

    try:
        conn = engine.connect()
    except Exception as e:
        print(e)
        exit(1)

    if conn is not None:
        print("Connected to the TDengine ...")
    else:
        print("Failed to connect to taos")
        exit(1)

    df = pd.read_sql(
        text("select _wstart as ds, avg(num) as y from power.meters interval(1w)"), conn
    )
    conn.close()

    df.insert(0, column="unique_id", value="unique_id")

    print("Forecasting ...")
    forecast = mlforecast.MLForecast(
        models=[LinearRegression(), lgb.LGBMRegressor()],
        freq="W",
        lags=[52],
        target_transforms=[Differences([52])],
    )
    forecast.fit(df)

    predicts = forecast.predict(52)

    pd.concat([df, predicts]).set_index("ds").plot(figsize=(12, 8))

    if args.dump:
        plt.savefig(args.dump)
    else:
        plt.show()
    print("Done")
