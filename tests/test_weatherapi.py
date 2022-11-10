import os

from app import app
from weatherapi import __version__

os.environ["TESTING"] = "1"


def test_version():
    assert __version__ == "0.1.0"


def test_view():
    with app.test_client() as c:
        r = c.get("/weather/Bauchi")
        assert r.status_code == 200
        assert len(r.json["data"]) == 7
        for forecast in r.json["data"]:
            assert len(forecast) == 5
            assert isinstance(forecast[-1], str)


def test_index():
    with app.test_client() as c:
        r = c.get("/")
        assert r.status_code == 200
