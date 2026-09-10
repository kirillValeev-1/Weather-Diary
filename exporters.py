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
    
def import_from_csv(path: str) -> List[WeatherRecord]:
    """Импорт записей из CSV-файла."""
    result: List[WeatherRecord] = []
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # пропустить заголовок
            for row in reader:
                if len(row) < 4:
                    continue
                try:
                    result.append(WeatherRecord(
                        date=row[0].strip(),
                        temperature=float(row[1]),
                        description=row[2].strip(),
                        precipitation=row[3].strip().lower() in ("да", "yes", "true", "1"),
                    ))
                except (ValueError, IndexError):
                    continue
    except OSError:
        return []
    return result