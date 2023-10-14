import sqlite3
from datetime import datetime
from model import Weather

connection = sqlite3.connect("logs.db")
cur = connection.cursor()

datetime_format = "%d.%m.%Y %H:%M:%S"


def create_database():
    query = """
    CREATE TABLE IF NOT EXISTS logs(
                query_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
                time TEXT,
                city TEXT,
                temperature REAL,
                feels_like REAL,
                description TEXT,
                wind REAL
                );
    """
    cur.execute(query)


def append_logs(weather: Weather):
    query = """
    INSERT INTO logs
      (time, city, temperature, feels_like, description, wind)
    VALUES
      (?, ?, ?, ?, ?, ?);
    """
    cur.execute(query, (
        weather.time.strftime(datetime_format),
        weather.city,
        weather.temperature,
        weather.feels_like,
        weather.description,
        weather.wind
    ))
    connection.commit()


def close_db_connection():
    connection.close()


def read_logs(limit: int):
    query = """
    SELECT * FROM logs ORDER BY query_id DESC LIMIT ?;
    """
    cur.execute(query, (str(limit),))
    rows = cur.fetchall()
    result = list(map(lambda row: Weather(
        time=datetime.strptime(row[1], datetime_format),
        city=row[2],
        temperature=row[3],
        feels_like=row[4],
        description=row[5],
        wind=row[6]
    ), rows))
    if len(result) < 10:
        for i in range(10 - len(result)):
            result.append(None)
    return result


create_database()
