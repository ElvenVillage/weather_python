import curses
from curses.textpad import rectangle
import geocoder
from os import getenv
from dotenv import load_dotenv

import network
from model import Weather
import db

menu = ["Обновить информацию о погоде",
        "Посмотреть историю запросов",
        "Изменить город",
        "Выход"
        ]


def get_my_city():
    loc = geocoder.ip("me")
    return loc.city


def draw_weather(stdscr, weather: Weather, start_line: int):
    if weather is not None:
        try:
            stdscr.addstr(start_line + 1, 2, "Текущее время: " +
                          weather.time.isoformat())
            stdscr.addstr(start_line + 2, 2,
                          "Название города: " + weather.city)
            stdscr.addstr(start_line + 3, 2, "Погодные условия: " +
                          weather.description)
            stdscr.addstr(start_line + 4, 2,
                          "Текущая температура: " + str(weather.temperature))
            stdscr.addstr(start_line + 5, 2, "Ощущается как: " +
                          str(weather.feels_like))
            stdscr.addstr(start_line + 6, 2,
                          "Скорость ветра: " + str(weather.wind))
            rectangle(stdscr, start_line, 0, start_line + 7, 60)
        except curses.error:
            pass


def draw_city(stdscr, city):
    try:
        stdscr.addstr(7, 0, "Текущее местоположение: ")
        stdscr.addstr(8, 0, city)
    except curses.error:
        pass


def draw_status_bar(stdscr, position: int, size: int):
    try:
        stdscr.addstr(9, 0, str(position + 1) + "/" + str(size))
    except curses.error:
        pass


def draw_input(stdscr, line, query):
    try:
        stdscr.addstr(line, 0, query)
    except curses.error:
        pass
    curses.echo()
    return str(stdscr.getstr(line, len(query), 80), 'UTF-8')


def draw_error(stdscr, error: str):
    try:
        rectangle(stdscr, 2, 2, 6 , 40)
        stdscr.addstr(4, 9, error)
    except curses.error:
        pass


def draw_menu(stdscr, selected):
    line_num = 1
    try:
        for line in menu:
                curses.setsyx(line_num, 0)
                stdscr.clrtoeol()
                if line == menu[selected]:
                    stdscr.addstr(line_num, 2, "> " + line)
                else:
                    stdscr.addstr(line_num, 2, "  " + line)
                line_num += 1
        rectangle(stdscr, 0, 0, 6, 40)
    except curses.error:
        pass


def fetch_weather_data(city) -> Weather:
    api_key = getenv("APIKEY")
    try:
        return network.fetch_weather(city, api_key)
    except Exception:
        return None



def main(stdscr):
    stdscr.clear()
    stdscr.keypad(True)

    selected = 0
    activated = None
    selected_log = 0

    city = get_my_city()
    weather = None
    logs = []
    logs_to_read = None
    error = None

    def draw():
        if error is not None:
            draw_error(stdscr, error)
            return
        
        draw_menu(stdscr, selected)
        draw_city(stdscr, city)

        if activated == 0 and weather is not None:
            draw_weather(stdscr, weather, 9)
        
        if activated == 1 and logs_to_read is not None and logs:
            draw_status_bar(stdscr, selected_log, len(logs))
            draw_weather(stdscr, logs[selected_log], 10)
    
    with db.create_connection() as connection:
        cur = connection.cursor()
        db.create_database(cur)

        while True:
            stdscr.clear()
            draw()
        

            key = stdscr.get_wch()
            if error is not None:
                error = None
                continue

            if key == curses.KEY_DOWN and selected < len(menu) - 1:
                selected += 1

            elif key == curses.KEY_UP and selected > 0:
                selected -= 1

            elif (key == curses.KEY_RIGHT and selected == 1 and
                selected_log < len(logs)-1):
                selected_log += 1
            elif key == curses.KEY_LEFT and selected == 1 and selected_log > 0:
                selected_log -= 1

            elif key == "\n":
                if selected == 0:
                    weather = fetch_weather_data(city)
                    activated = selected
                    db.append_logs(cur, weather)
                    connection.commit()

                elif selected == 1:
                    logs_to_read = None
                    weather = None
                    stdscr.clear()
                    draw()
                    try:
                        logs_to_read = draw_input(stdscr, 9, "Введите количество записей: ")
                        logs = db.read_logs(cur, limit=logs_to_read)
                        selected_log = 0
                        activated = selected
                    except:
                        error = "Повторите попытку"
                    
                        
                elif selected == 2:
                    logs_to_read = None
                    weather = None
                    stdscr.clear()
                    draw()
                    try:
                        city = draw_input(stdscr, 9, "Введите город: ")
                        weather = fetch_weather_data(city)
                        db.append_logs(cur, weather)
                        connection.commit()
                        activated = 0
                    except:
                        error = "Повторите попытку"
    
                elif selected == 3:
                    break
        stdscr.refresh()



if __name__ == "__main__":
    load_dotenv()
    curses.wrapper(main)
