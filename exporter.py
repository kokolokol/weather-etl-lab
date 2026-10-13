import os

from dotenv import load_dotenv
from sqlalchemy import select
from db_models import WeatherForecast
load_dotenv()
def save_data(session, city, days):
    # сохраняем записи, пропуская уже существующие
    added = 0
    for d in days:
        exists = session.execute(
            select(WeatherForecast).where(
                WeatherForecast.city == city,
                WeatherForecast.forecast_date == d["date"],
            )
        ).scalar_one_or_none()

        if exists:
            continue

        session.add(WeatherForecast(
            city=city,
            forecast_date=d["date"],
            temp_min=d["temp_min"],
            temp_max=d["temp_max"],
            humidity=d["humidity"],
            wind_speed=d["wind_speed"],
            description=d["description"],
        ))
        added += 1

    session.commit()
    print("Добавлено записей:", added)
    return added


def export_md(session, city):
    # выгружаем прогноз города в markdown-файл
    rows = session.execute(
        select(WeatherForecast)
        .where(WeatherForecast.city == city)
        .order_by(WeatherForecast.forecast_date)
    ).scalars().all()

    if not rows:
        print("Нет данных города", city)
        return None

    filename = os.getenv("OUTPUT_FILE", "weather_report.md")

    # формат даты как в РФ: дд-мм-гггг
    fmt = "%d-%m-%Y"
    period_start = rows[0].forecast_date.strftime(fmt)
    period_end = rows[-1].forecast_date.strftime(fmt)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Прогноз погоды\n\n")
        f.write("Локация: " + city + "\n\n")
        f.write("Период: " + period_start + " — " + period_end + "\n\n")
        f.write("| Дата | Мин. темп. (°C) | Макс. темп. (°C) | "
                "Описание | Влажность (%) | Ветер (м/с) |\n")
        f.write("|------|------|------|------|------|------|\n")
        for r in rows:
            d = r.forecast_date.strftime(fmt)
            f.write(f"| {d} | {r.temp_min:.1f} | {r.temp_max:.1f} | "
                    f"{r.description} | {r.humidity} | {r.wind_speed:.1f} |\n")

    print("Файл сохранён:", filename)
    return filename