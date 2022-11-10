import pandas as pd
import pytest

from weatherapi.extract_transform import preprocess_data, scrape_location


@pytest.mark.parametrize(("location", "lagperiod"), [["Bauchi", 2], ["Lokoja", 10]])
def test_scrape(location, lagperiod):
    raw_data = scrape_location(location, lagperiod)
    assert len(raw_data) == lagperiod


@pytest.mark.parametrize(("location", "lagperiod"), [["Bauchi", 2], ["Lokoja", 10]])
def test_preprocess_data(location, lagperiod):
    raw_data = scrape_location(location, lagperiod)
    assert isinstance(preprocess_data(raw_data), pd.DataFrame)
