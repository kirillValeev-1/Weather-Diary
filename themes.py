"""Цветовые темы приложения."""

LIGHT = {
    "bg": "#f0f0f0",
    "fg": "#000000",
    "panel": "#e0e8f0",
    "button_bg": "#ffffff",
    "table_bg": "white",
    "header_bg": "lightgray",
    "status_bg": "#ffffcc",
}

DARK = {
    "bg": "#2b2b2b",
    "fg": "#e0e0e0",
    "panel": "#3c3f41",
    "button_bg": "#4a4a4a",
    "table_bg": "#1e1e1e",
    "header_bg": "#555555",
    "status_bg": "#3a3a3a",
}


def get_theme(name: str) -> dict:
    return DARK if name == "dark" else LIGHT