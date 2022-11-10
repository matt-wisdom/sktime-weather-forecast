import numpy as np
import pandas as pd
from sktime.classification.distance_based import KNeighborsTimeSeriesClassifier

from weatherapi.scraper import scrape
from weatherapi.weather_forecaster import *

df = scrape("Random", 500)


def test_generate_ts_classification_data():
    window = 30
    df["condition_labels"] = list(range(len(df)))
    X, y = generate_ts_classification_data(df, window)
    assert isinstance(X, np.ndarray)
    assert isinstance(y, pd.Series)

    assert X.shape[1] == 5
    assert X.shape[2] == window


def test_generate_ts_prediction_X():
    window = 30
    df["condition_labels"] = list(range(len(df)))
    X = generate_ts_prediction_X(df, window)
    assert isinstance(X, np.ndarray)

    assert X.shape[0] == 1
    assert X.shape[1] == 5
    assert X.shape[2] == window


def test_create_condition_predictor():
    pred, le, data = create_condition_predictor(df)
    assert isinstance(pred, KNeighborsTimeSeriesClassifier)
    assert (
        le.
        inverse_transform(data.condition_labels)
        .tolist() == df["conditions"].to_list()
    )


def test_make_forecaster():
    forecaster = make_forecaster(df)
    assert len(forecaster.predict([1, 2, 3, 4])) == 4
