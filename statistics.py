"""Расчёт статистики по записям о погоде."""
from typing import List, Optional
from models import WeatherRecord


def average_temperature(records: List[WeatherRecord]) -> Optional[float]:
    if not records:
        return None
    return round(sum(r.temperature for r in records) / len(records), 2)


def min_temperature(records: List[WeatherRecord]) -> Optional[float]:
    if not records:
        return None
    return min(r.temperature for r in records)


def max_temperature(records: List[WeatherRecord]) -> Optional[float]:
    if not records:
        return None
    return max(r.temperature for r in records)


def precipitation_days(records: List[WeatherRecord]) -> int:
    return sum(1 for r in records if r.precipitation)


def summary(records: List[WeatherRecord]) -> str:
    if not records:
        return "Записей пока нет"
    return (
        f"Всего: {len(records)} | "
        f"Средняя: {average_temperature(records)}°C | "
        f"Мин: {min_temperature(records)}°C | "
        f"Макс: {max_temperature(records)}°C | "
        f"Дней с осадками: {precipitation_days(records)}"
    )