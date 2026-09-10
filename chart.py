"""Отрисовка мини-графика температур на tk.Canvas."""
from typing import List
import tkinter as tk
from models import WeatherRecord


def draw_temperature_chart(canvas: tk.Canvas, records: List[WeatherRecord],
                            width: int = 900, height: int = 180) -> None:
    """Рисует линейный график температур по датам."""
    canvas.delete("all")

    if not records:
        canvas.create_text(width // 2, height // 2,
                           text="Нет данных для графика",
                           fill="gray", font=("Arial", 10, "italic"))
        return

    sorted_records = sorted(records, key=lambda r: r.date)
    temps = [r.temperature for r in sorted_records]
    t_min, t_max = min(temps), max(temps)

    # Нулевая линия должна быть учтена
    t_min = min(t_min, 0)
    t_max = max(t_max, 0)
    span = (t_max - t_min) or 1.0

    margin_left = 40
    margin_right = 20
    margin_top = 15
    margin_bottom = 30

    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    # Оси
    canvas.create_line(margin_left, margin_top,
                       margin_left, height - margin_bottom,
                       fill="#888")
    canvas.create_line(margin_left, height - margin_bottom,
                       width - margin_right, height - margin_bottom,
                       fill="#888")

    # Подписи осей
    canvas.create_text(10, margin_top, text=f"{t_max:.0f}°",
                       anchor="w", fill="#555", font=("Arial", 8))
    canvas.create_text(10, height - margin_bottom, text=f"{t_min:.0f}°",
                       anchor="w", fill="#555", font=("Arial", 8))

    # Нулевая линия, если диапазон охватывает 0
    if t_min <= 0 <= t_max:
        y_zero = margin_top + (t_max / span) * plot_h
        canvas.create_line(margin_left, y_zero, width - margin_right, y_zero,
                           fill="#bbb", dash=(3, 3))

    n = len(sorted_records)
    step_x = plot_w / max(n - 1, 1)
    points = []

    for i, rec in enumerate(sorted_records):
        x = margin_left + i * step_x
        y = margin_top + (1 - (rec.temperature - t_min) / span) * plot_h
        points.append((x, y))

    # Линия
    for i in range(1, len(points)):
        x1, y1 = points[i - 1]
        x2, y2 = points[i]
        canvas.create_line(x1, y1, x2, y2, fill="#4a90d9", width=2)

    # Точки + температура над каждой
    for i, (x, y) in enumerate(points):
        color = "#d9534f" if sorted_records[i].temperature < 0 else "#5cb85c"
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline="")
        if n <= 20:
            canvas.create_text(x, y - 12, text=f"{sorted_records[i].temperature:.0f}",
                               fill="#333", font=("Arial", 7))