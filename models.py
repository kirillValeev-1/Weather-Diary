"""Модели данных для Weather Diary."""
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class WeatherRecord:
    """Запись о погоде за один день."""
    date: str
    temperature: float
    description: str
    precipitation: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "WeatherRecord":
        return cls(
            date=data["date"],
            temperature=float(data["temperature"]),
            description=data["description"],
            precipitation=bool(data.get("precipitation", False)),
        )

    def formatted_date(self) -> str:
        """Возвращает дату в формате ДД.ММ.ГГГГ."""
        try:
            dt = datetime.strptime(self.date, "%Y-%m-%d")
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            return self.date

    def precip_text(self) -> str:
        return "Да" if self.precipitation else "Нет"

    def __str__(self) -> str:
        return f"{self.formatted_date()}: {self.temperature}°C, {self.description}"
    

    def weather_emoji(self) -> str:
   
        if self.precipitation and self.temperature <= 0:
            return "❄️"
        if self.precipitation:
            return "🌧️"
        if self.temperature >= 25:
            return "☀️"
        if self.temperature >= 10:
            return "🌤️"
        return "☁️"
