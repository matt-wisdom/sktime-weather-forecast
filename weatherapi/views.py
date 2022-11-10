import time
import datetime
import flask
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from weatherapi.scraper import scrape
from weatherapi.weather_forecaster import main_forecaster

app = flask.Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': '/tmp/weatherapi'})
limiter = Limiter(app, key_func=get_remote_address, default_limits=["16/minute"])

with app.app_context():
    # Clear cache on first run
    cache.clear()

lag = 1500
cache_time = 8*3600 # Cache city prediction for 8 hours

@cache.memoize(cache_time)
def predict(location):
    data = scrape(location, lag)
    if data is None:
        flask.abort(flask.Response('{"message": "Invalid Location"}', 400))
    forecast = main_forecaster(data)
    return forecast

@app.get("/")
def index():
    return flask.render_template("index.html")

@app.get("/weather/<location>")
def getweather(location: str):
    forecast = predict(location)
    dates = [datetime.date.fromtimestamp(time.time()+i*86400).isoformat() for i in range(7)]
    return flask.jsonify({"data": forecast.to_numpy().tolist(), "dates": dates})
