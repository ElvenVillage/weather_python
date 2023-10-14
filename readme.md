## Информация о погоде
Используем API OpenWeatherMap
```
https://api.openweathermap.org/data/2.5/weather
```
с параметрами
```
{
    "q": {CITY},
    "appid": {APIKEY},
    "lang": "ru",
    "units": "metric"
}
```
## Местоположение
Использую пакет `geocoder`:
```
def get_city():
    loc = geocoder.ip("me")
    return loc.city
```
## Хранение истории
Для хранения использую таблицу в базе SQLite. Для пользователя доступны последние 10 запросов
## Интерфейс
Управление стрелочками (←→ для выбора из списка запросов, ↓↑ для выбора из меню). Для подтверждения нажать на пробел
