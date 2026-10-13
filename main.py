from geo_locator import get_location
from weather_client import get_forecast, group_by_days
from db_models import init_db, get_session
from exporter import save_data, export_md


def main():
    city, lat, lon = get_location()

    try:
        data = get_forecast(lat, lon, city)
    except Exception as e:
        print("Ошибка при запросе погоды:", e)
        return

    days, api_city = group_by_days(data)
    city = api_city or city
    if not days:
        print("Прогноза нет")
        return
    try:
        engine = init_db()
        session = get_session(engine)

        added = save_data(session, city, days)
        path = export_md(session, city)

        session.close()
    except Exception as e:
        print("Ошибка при работе с БД:", e)
        return
    fmt = "%d-%m-%Y"
    print()
    print("Город:", city)
    print("Координаты:", lat, lon)
    print("Период:", days[0]["date"].strftime(fmt), "—",
          days[-1]["date"].strftime(fmt))
    print("Записей добавлено:", added)
    print("Файл:", path)

if __name__ == "__main__":
    main()