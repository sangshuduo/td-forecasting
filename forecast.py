import argparse

import gif
import lightgbm as lgb
import matplotlib.pyplot as plt
import mlforecast
import pandas as pd
import plotext
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
    parser.add_argument(
        "--gif", type=str, help="dump forecast picture to gif file", required=False
    )

    parser.add_argument(
        "--plotext",
        action="store_true",
        help="plot forecast picture in console mode",
        required=False,
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
        text(
            "select _wstart as ds, avg(num) as y, avg(temperature) as temperature, avg(goods) as goods from power.meters interval(1w)"
        ),
        conn,
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

    if not args.dump:
        if args.plotext:
            plotext.scatter(df)
            plotext.show()
        else:
            fig = plt.figure()
            timer = fig.canvas.new_timer(interval=5000)
            timer.add_callback(plt.close)
            df.set_index("ds").plot(
                figsize=(12, 8), title="current data, will disappear in 5 sec"
            )

            timer.start()
            plt.show()
            timer.stop()

    pd.concat([df, predicts]).set_index("ds").plot(
        figsize=(12, 8), title="current data with forecast"
    )

    if args.dump:
        plt.savefig(args.dump)
    elif args.gif:
        # TODO: add gif support
        gif.options.matplotlib["dpi"] = 300
        # gif.save(frames, "output.gif", duration=50)
    elif args.plotext:
        plotext.show()
    else:
        plt.show()
    print("Done")
