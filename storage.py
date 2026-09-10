"""Работа с JSON-хранилищем записей о погоде."""
import json
import os
from typing import List
from models import WeatherRecord

DATA_FILE = "weather.json"


def load_records(path: str = DATA_FILE) -> List[WeatherRecord]:
    """Загрузка записей из JSON. Возвращает пустой список при ошибке."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [WeatherRecord.from_dict(item) for item in raw]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Ошибка загрузки: {e}")
        return []


def save_records(records: List[WeatherRecord], path: str = DATA_FILE) -> bool:
    """Сохраняет записи в JSON. Возвращает True при успехе."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                [r.to_dict() for r in records],
                f,
                ensure_ascii=False,
                indent=2,
            )
        return True
    except OSError as e:
        print(f"Ошибка сохранения: {e}")
        return False