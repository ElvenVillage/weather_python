import requests
from datetime import datetime
from model import Weather
from db import append_logs

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city_name: str, APIKEY: str) -> Weather:
    query = {
        "q": city_name,
        "appid": APIKEY,
        "lang": "ru",
        "units": "metric"
    }
    response = requests.get(BASE_URL, params=query).json()
    weather = Weather(
        time=datetime.now(),
        city=city_name,
        temperature=response["main"]["temp"],
        feels_like=response["main"]["feels_like"],
        description=response["weather"][0]["description"],
        wind=response["wind"]["speed"]
    )
    append_logs(weather)
    return weather
