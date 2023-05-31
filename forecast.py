import mlforecast
from mlforecast.target_transforms import Differences
from sklearn.linear_model import LinearRegression
from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
    engine = create_engine("taos://root:taosdata@localhost:6030/power")
    conn = engine.connect()
    df = pd.read_sql(
        text("select _wstart as ds, avg(num) as y from power.meters interval(1w)"), conn
    )
    conn.close()

    df.insert(0, column="unique_id", value="unique_id")

    forecast = mlforecast.MLForecast(
        models=LinearRegression(),
        freq="W",
        lags=[52],
        target_transforms=[Differences([52])],
    )
    forecast.fit(df)

    predicts = forecast.predict(52)

    pd.concat([df, predicts]).set_index("ds").plot(figsize=(12, 8))
    plt.show()
