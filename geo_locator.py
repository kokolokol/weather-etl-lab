# определяем город по IP через ipinfo.io
# если не получилось — берём из .env (GEO_API_FALLBACK_CITY)

import os
import requests
from dotenv import load_dotenv

load_dotenv()
def get_location():
    # город широта долгота
    url = os.getenv("GEO_API_URL", "https://ipinfo.io/json")
    fallback = os.getenv("GEO_API_FALLBACK_CITY", "Moscow")

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        city = data.get("city") # название города
        loc = data.get("loc")  # координаты
        if city and loc:
            lat, lon = loc.split(",")
            print("Город определён:", city)
            return city, float(lat), float(lon)

        print("В ответе нет города или координат, беру fallback")

    except Exception as e:
        print("Не получилось определить гео:", e)

    print("Использую город по умолчанию:", fallback)
    return fallback, None, None