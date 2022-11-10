from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import LabelEncoder
from sktime.classification.distance_based import KNeighborsTimeSeriesClassifier
from sktime.forecasting.compose import EnsembleForecaster, make_reduction
from xgboost import XGBRegressor

# from sktime.forecasting.var import VAR


def main_forecaster(data: pd.DataFrame, fh: list = list(range(1, 8))) -> pd.DataFrame:
    """
    Put everything together
    """
    forecaster = make_forecaster(data)

    # Forecast is DataFrame with cols tempmax, tempmin
    # dew, humidity
    forecast = forecaster.predict(fh)
    print(forecast)
    # For each forecast predict the weather condition
    knn, le, data = create_condition_predictor(data)
    forecast.index = list(range(len(forecast)))
    conditions = []
    for i in range(len(fh)):
        pred = knn.predict(generate_ts_prediction_X(data))
        forecast_i = forecast.iloc[i]
        new = {
            "tempmax": forecast_i.tempmax,
            "tempmin": forecast_i.tempmin,
            "dew": forecast_i.dew,
            "humidity": forecast_i.humidity,
            "condition_labels": pred[0],
        }
        conditions.append(pred[0])
        data = data.append(new, ignore_index=True)
    conditions = pd.DataFrame({"conditions": le.inverse_transform(conditions)})
    return forecast.join(conditions)


def make_forecaster(data: pd.DataFrame) -> EnsembleForecaster:
    """
    Create a forecaster to forecast temperatures, dew point
    and humidity for location data
    """
    regressor = KNeighborsRegressor(n_neighbors=1)
    knn_forecaster = make_reduction(regressor, window_length=30, strategy="recursive")
    xgb_forecaster = make_reduction(
        XGBRegressor(), window_length=60, strategy="recursive"
    )
    # var_forecaster = VAR(60, trend="c", random_state=43, ic="aic")

    forecaster = EnsembleForecaster(
        [
            ("knn", knn_forecaster),
            ("xgb", xgb_forecaster),
        ]
    )
    cols = ["tempmax", "tempmin", "dew", "humidity"]
    forecaster.fit(data[cols].asfreq("D"))
    return forecaster


def create_condition_predictor(
    data: pd.DataFrame,
) -> Tuple[KNeighborsTimeSeriesClassifier, LabelEncoder, pd.DataFrame]:
    """
    Train a sktime classifier for weather condition.
    """
    le = LabelEncoder().fit(data.conditions)
    data["condition_labels"] = le.transform(data.conditions)
    X, y = generate_ts_classification_data(data)
    hc2 = KNeighborsTimeSeriesClassifier()
    hc2.fit(X, y)
    return hc2, le, data


def generate_ts_prediction_X(df: pd.DataFrame, window: int = 60) -> np.array:
    start = len(df)
    data = df.iloc[start - window:][
        ["tempmax", "tempmin", "dew", "humidity", "condition_labels"]
    ].values.T
    return np.array([data])


def generate_ts_classification_data(
    df: pd.DataFrame, window: int = 60
) -> Tuple[np.array, pd.Series]:
    """
    Generate data for predicting weather condition
    using previous days weather data
    """
    X = []
    y = []
    length = len(df)
    idx = list(range(window + 1, length - window))
    for i in idx:
        prev = df.iloc[i - window - 1:i - 1]
        X.append(
            [
                prev.tempmax.values,
                prev.tempmin.values,
                prev.dew.values,
                prev.humidity.values,
                prev.condition_labels.values,
            ]
        )
        y.append(df.iloc[i].condition_labels)
    return np.array(X), pd.Series(y)
