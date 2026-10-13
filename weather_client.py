import os
from collections import defaultdict
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()


def get_forecast(lat, lon, city=None):
    #прогноз на 5 дней от OpenWeatherMap

    key = os.getenv("WEATHER_API_KEY")
    base = os.getenv("WEATHER_API_BASE_URL",
                     "https://api.openweathermap.org/data/2.5/forecast")

    if not key:
        raise Exception("В .env нет WEATHER_API_KEY")

    params = {
        "appid": key,
        "units": "metric",
        "lang": "ru",
    }
    if lat and lon:
        params["lat"] = lat
        params["lon"] = lon
    elif city:
        params["q"] = city
    else:
        raise Exception("Нужны координаты или город")

    try:
        r = requests.get(base, params=params, timeout=15)
    except Exception as e:
        raise Exception("Сеть недоступна: " + str(e))

    if r.status_code == 401:
        raise Exception("Неверный API-ключ (401)")
    if r.status_code == 404:
        raise Exception("Город не найден (404)")
    if r.status_code == 429:
        raise Exception("Слишком много запросов (429)")

    data = r.json()
    if str(data.get("cod")) != "200":
        raise Exception("Ошибка API: " + str(data.get("message")))

    print("Получено точек:", len(data["list"]))
    return data


def group_by_days(data):
    # группируем 3-часовые точки по датам, оставляем 4 дня
    days_map = defaultdict(list)

    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        days_map[dt.date()].append((dt, item))

    today = datetime.now().date()
    days = sorted(d for d in days_map if d >= today)[:4]

    result = []
    for day in days:
        points = days_map[day]

        tmin = min(p["main"]["temp_min"] for _, p in points)
        tmax = max(p["main"]["temp_max"] for _, p in points)
        hum = sum(p["main"]["humidity"] for _, p in points) / len(points)
        wind = max(p["wind"]["speed"] for _, p in points)

        # описание берём у точки, ближайшей к 12:00
        noon = min(points, key=lambda x: abs(x[0].hour - 12))
        desc = noon[1]["weather"][0]["description"]

        result.append({
            "date": day,
            "temp_min": tmin,
            "temp_max": tmax,
            "humidity": round(hum),
            "wind_speed": wind,
            "description": desc,
        })

    city_name = data["city"]["name"]
    print("Дней в прогнозе:", len(result))
    return result, city_name