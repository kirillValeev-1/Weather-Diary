"""Экспорт и импорт записей о погоде."""
import csv
from typing import List
from models import WeatherRecord


def export_to_csv(records: List[WeatherRecord], path: str = "weather_export.csv") -> bool:
    """Экспорт записей в CSV-файл."""
    try:
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Дата", "Температура", "Описание", "Осадки"])
            for r in records:
                writer.writerow([r.date, r.temperature, r.description, r.precip_text()])
        return True
    except OSError:
        return False


def export_to_txt(records: List[WeatherRecord], path: str = "weather_export.txt") -> bool:
    """Экспорт записей в текстовый файл."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(f"{r.formatted_date()} — {r.temperature}°C — {r.description} "
                        f"(осадки: {r.precip_text()})\n")
        return True
    except OSError:
        return False