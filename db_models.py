import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (Column, Integer, String, Float, Date, DateTime,
                        UniqueConstraint, create_engine)
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

Base = declarative_base()


class WeatherForecast(Base):
    __tablename__ = "weather_forecast"

    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String, nullable=False)
    forecast_date = Column(Date, nullable=False)
    temp_min = Column(Float)
    temp_max = Column(Float)
    humidity = Column(Integer)
    wind_speed = Column(Float)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # пара "город + дата" должна быть уникальной
    __table_args__ = (UniqueConstraint("city", "forecast_date"),)


def init_db():
    db_url = os.getenv("DB_URL", "sqlite:///weather_lab.db")
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()