import requests
import datetime
from model import Weather

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city_name: str, APIKEY: str) -> Weather:
    query = {
        "q": city_name,
        "appid": APIKEY,
        "lang": "ru",
        "units": "metric"
    }
    response = requests.get(BASE_URL, params=query).json()
    if "main" in response:
        time = datetime.datetime.fromtimestamp(response["dt"], datetime.timezone.utc)
        timezone = datetime.timezone(datetime.timedelta(seconds=response["timezone"]))
        weather = Weather(
            time=time.astimezone(timezone),
            city=city_name,
            temperature=response["main"]["temp"],
            feels_like=response["main"]["feels_like"],
            description=response["weather"][0]["description"],
            wind=response["wind"]["speed"]
        )
        return weather
    else:
        raise Exception('Некорректный запрос')
