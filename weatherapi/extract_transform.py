import datetime
import time

import pandas as pd
import requests

url = "https://weather.visualcrossing.com/"
url += "VisualCrossingWebServices/rest/services"
url += "/timeline/{location}/{date}/2022-11-16?unitGroup=metric&"
url += "key=ZMM2U9XUSJ6UV37L4L49NQACY&options=preview&contentType=json"


def scrape_location(location: str, lag: int = 120) -> list:  # 120days
    """
        Get location data
    """
    days_data = []
    # Convert lag from days to seconds
    lag = lag * 86400
    date = datetime.date.fromtimestamp(time.time() - lag).isoformat()
    try:
        data = requests.get(url.format(location=location, date=date)).json()
    except requests.exceptions.JSONDecodeError:
        return None

    while True:
        try:
            for day in data["days"]:
                if datetime.date.fromisoformat(
                    day["datetime"]
                ) < datetime.date.fromisoformat(date):
                    continue
                if datetime.date.fromisoformat(
                    day["datetime"]
                ) >= datetime.date.fromtimestamp(time.time()):
                    return days_data
                days_data.append(day)
            last = data["days"][-1]["datetime"]
            if last == date:
                break
            date = last
            data = requests.get(url.format(location=location, date=date)).json()
        except Exception as e:
            print(e)
            break
    return days_data


def preprocess_data(days_data: list) -> pd.DataFrame:
    """
    Convert raw data to multivariate time series
    """
    processed = []
    for row in days_data:
        if "hours" in row:
            row.pop("hours")
        processed.append(row)

    df = pd.DataFrame(processed)
    df = df.drop(columns=["snow", "snowdepth"])
    df = df.fillna(df.median())

    df.datetime = pd.to_datetime(df.datetime, format="%Y-%m-%d", utc=True)
    df = df.set_index("datetime")
    df.index = pd.to_datetime(df.index.date)

    # Remove duplicate rows
    to = datetime.date.fromtimestamp(time.time()).isoformat()
    df = df[~df.index.duplicated()].loc[:to]
    return df


def scrape(location: str, lag: int) -> pd.DataFrame:
    days_data = scrape_location(location, lag)
    if days_data:
        return preprocess_data(days_data)
