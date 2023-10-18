import sqlite3
from contextlib import contextmanager
from datetime import datetime
from model import Weather

@contextmanager
def create_connection():
    connection = sqlite3.connect("logs.db")
    yield connection
    connection.close()



def create_database(cur):
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


def append_logs(cur, weather: Weather):
    query = """
    INSERT INTO logs
      (time, city, temperature, feels_like, description, wind)
    VALUES
      (?, ?, ?, ?, ?, ?);
    """
    cur.execute(query, (
        weather.time.isoformat(),
        weather.city,
        weather.temperature,
        weather.feels_like,
        weather.description,
        weather.wind
    ))


def read_logs(cur, limit: int):
    query = """
    SELECT * FROM logs ORDER BY query_id DESC LIMIT ?;
    """
    cur.execute(query, (str(limit),))
    rows = cur.fetchall()
    return list(map(lambda row: Weather(
        time=datetime.fromisoformat(row[1]),
        city=row[2],
        temperature=row[3],
        feels_like=row[4],
        description=row[5],
        wind=row[6]
    ), rows))
