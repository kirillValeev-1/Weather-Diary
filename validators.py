"""Функции валидации пользовательского ввода."""
from datetime import datetime


def validate_date(date_str: str) -> bool:
    """Проверяет дату в формате ГГГГ-ММ-ДД."""
    if not date_str:
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_temperature(temp_str: str) -> bool:
    """Проверяет, что строка — корректное число."""
    if temp_str is None or temp_str == "":
        return False
    try:
        float(temp_str)
        return True
    except ValueError:
        return False


def validate_description(desc: str) -> bool:
    """Описание не должно быть пустым."""
    return bool(desc and desc.strip())


def validate_record(date: str, temp: str, desc: str) -> tuple[bool, str]:
    """Комплексная проверка. Возвращает (успех, сообщение об ошибке)."""
    if not validate_date(date):
        return False, "Дата должна быть в формате ГГГГ-ММ-ДД!"
    if not validate_temperature(temp):
        return False, "Температура должна быть числом!"
    if not validate_description(desc):
        return False, "Описание не должно быть пустым!"
    return True, ""