import curses
import geocoder
from os import getenv
from dotenv import load_dotenv

import network
from model import Weather
from db import read_logs, close_db_connection

menu = ["Обновить информацию о погоде",
        "Посмотреть историю запросов", "Изменить город", "Выход"]


def get_my_city():
    loc = geocoder.ip("me")
    return loc.city


def draw_weather(stdscr, weather: Weather, start_line: int):
    if weather is not None:
        try:
            stdscr.addstr(start_line, 0, "Текущее время: " +
                          weather.time.strftime("%d.%m.%Y %H:%M:%S"))
            stdscr.addstr(start_line + 1, 0,
                          "Название города: " + weather.city)
            stdscr.addstr(start_line + 2, 0, "Погодные условия: " +
                          weather.description)
            stdscr.addstr(start_line + 3, 0,
                          "Текущая температура: " + str(weather.temperature))
            stdscr.addstr(start_line + 4, 0, "Ощущается как: " +
                          str(weather.feels_like))
            stdscr.addstr(start_line + 5, 0,
                          "Скорость ветра: " + str(weather.wind))
        except curses.error:
            pass


def draw_city(stdscr, city):
    try:
        stdscr.addstr(5, 0, "Текущее местоположение: ")
        stdscr.addstr(6, 0, city)
    except curses.error:
        pass


def draw_status_bar(stdscr, position: int, size: int):
    try:
        stdscr.addstr(7, 0, str(position) + "/" + str(size))
    except curses.error:
        pass


def draw_input(stdscr, line):
    curses.echo()
    return str(stdscr.getstr(line, 0, 80), 'UTF-8')


drawers = {
    0: draw_weather,
    1: draw_weather,
}


def fetch_weather_data(city) -> Weather:
    api_key = getenv("APIKEY")
    try:
        return network.fetch_weather(city, api_key)
    except Exception:
        return None


def load_logs():
    pass


def draw_menu(stdscr, selected):
    line_num = 0
    for line in menu:
        try:
            curses.setsyx(line_num, 0)
            stdscr.clrtoeol()
            if line == menu[selected]:
                stdscr.addstr(line_num, 0, "> " + line)
            else:
                stdscr.addstr(line_num, 0, "  " + line)
            line_num += 1
        except curses.error:
            pass


def main(stdscr):
    stdscr.clear()
    stdscr.keypad(True)
    selected = 0
    activated = None

    selected_log = 0

    city = get_my_city()
    weather = None
    logs = [None for i in range(10)]

    while True:
        stdscr.clear()
        drawer_params = {0: (weather, 8), 1: (logs[selected_log], 9)}
        draw_menu(stdscr, selected)
        draw_city(stdscr, city)
        if activated in drawers:
            drawers[activated](stdscr, *drawer_params[activated])
        if (activated == 1):
            draw_status_bar(stdscr, selected_log + 1, len(logs))

        key = stdscr.getch()
        if key == curses.KEY_DOWN and selected < len(menu) - 1:
            selected += 1

        elif key == curses.KEY_UP and selected > 0:
            selected -= 1

        elif (key == curses.KEY_RIGHT and selected == 1 and
              selected_log < len(logs)-1):
            selected_log += 1
        elif key == curses.KEY_LEFT and selected == 1 and selected_log > 0:
            selected_log -= 1

        elif key == ord(" "):
            if selected == 0:
                weather = fetch_weather_data(city)
            elif selected == 1:
                logs = read_logs(limit=10)
            elif selected == 2:
                input_line = 7
                if activated == 1:
                    input_line = 8
                city = draw_input(stdscr, input_line)
                curses.setsyx(6, 0)
                stdscr.clrtoeol()
            elif selected == 3:
                break
            activated = selected
        stdscr.refresh()
    close_db_connection()


if __name__ == "__main__":
    load_dotenv()
    curses.wrapper(main)
