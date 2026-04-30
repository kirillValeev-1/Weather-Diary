import json
import os
import tkinter as tk
from datetime import datetime

# Глобальные переменные
data_file = "weather.json"
records = []
current_filter_date = ""
current_filter_temp = None

def load_data():
    """Загрузка данных из JSON файла"""
    global records
    try:
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
        else:
            records = []
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        records = []

def save_data():
    """Сохранение данных в JSON файл"""
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def validate_date(date_str):
    """Проверка корректности даты в формате ГГГГ-ММ-ДД"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_temperature(temp_str):
    """Проверка, является ли строка числом (температура)"""
    try:
        float(temp_str)
        return True
    except ValueError:
        return False

def clear_table(table_frame):
    """Очистка таблицы"""
    for widget in table_frame.winfo_children():
        widget.destroy()

def display_records(table_frame, record_list):
    """Отображение записей погоды в таблице"""
    clear_table(table_frame)
    
    # Заголовки
    headers = ["Дата", "Температура", "Описание", "Осадки"]
    for col, header in enumerate(headers):
        label = tk.Label(table_frame, text=header, font=("Arial", 10, "bold"), 
                        borderwidth=1, relief="solid", padx=10, pady=5, bg="lightgray")
        label.grid(row=0, column=col, sticky="nsew")
    
    # Данные
    for row, rec in enumerate(record_list, start=1):
        tk.Label(table_frame, text=rec["date"], borderwidth=1, relief="solid", padx=10, pady=5).grid(row=row, column=0, sticky="nsew")
        tk.Label(table_frame, text=str(rec["temperature"]), borderwidth=1, relief="solid", padx=10, pady=5).grid(row=row, column=1, sticky="nsew")
        tk.Label(table_frame, text=rec["description"], borderwidth=1, relief="solid", padx=10, pady=5).grid(row=row, column=2, sticky="nsew")
        precip_text = "Да" if rec.get("precipitation", False) else "Нет"
        tk.Label(table_frame, text=precip_text, borderwidth=1, relief="solid", padx=10, pady=5).grid(row=row, column=3, sticky="nsew")
    
    # Настройка веса столбцов
    for col in range(4):
        table_frame.columnconfigure(col, weight=1)

def refresh_table(table_frame):
    """Обновление таблицы с учетом фильтрации"""
    filtered = filter_records()
    display_records(table_frame, filtered)

def filter_records():
    """Фильтрация записей по дате и температуре"""
    global current_filter_date, current_filter_temp
    
    filtered = records.copy()
    
    # Фильтр по дате
    if current_filter_date:
        filtered = [r for r in filtered if r["date"] == current_filter_date]
    
    # Фильтр по температуре (выше заданного порога)
    if current_filter_temp is not None:
        filtered = [r for r in filtered if r["temperature"] > current_filter_temp]
    
    return filtered

def add_record(date_entry, temp_entry, desc_entry, precip_var, table_frame):
    """Добавление новой записи о погоде"""
    date = date_entry.get().strip()
    temp = temp_entry.get().strip()
    desc = desc_entry.get().strip()
    precipitation = precip_var.get()  # True/False из чекбокса
    
    # Проверка полей
    if not validate_date(date):
        status_label.config(text="Ошибка: Дата должна быть в формате ГГГГ-ММ-ДД!", fg="red")
        return
    if not validate_temperature(temp):
        status_label.config(text="Ошибка: Температура должна быть числом!", fg="red")
        return
    if not desc:
        status_label.config(text="Ошибка: Описание не должно быть пустым!", fg="red")
        return
    
    # Добавление записи
    record = {
        "date": date,
        "temperature": float(temp),
        "description": desc,
        "precipitation": precipitation
    }
    records.append(record)
    save_data()
    
    # Очистка полей
    date_entry.delete(0, tk.END)
    temp_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)
    precip_var.set(False)
    
    status_label.config(text=f"Запись за {date} добавлена!", fg="green")
    refresh_table(table_frame)

def filter_by_date(filter_date_entry, table_frame):
    """Фильтрация по дате"""
    global current_filter_date
    date_str = filter_date_entry.get().strip()
    if date_str and not validate_date(date_str):
        status_label.config(text="Ошибка: Неверный формат даты для фильтра!", fg="red")
        return
    current_filter_date = date_str
    refresh_table(table_frame)
    
    if current_filter_date:
        status_label.config(text=f"Фильтр по дате: {current_filter_date}", fg="blue")
    else:
        status_label.config(text="Фильтр по дате сброшен", fg="blue")

def filter_by_temp(filter_temp_entry, table_frame):
    """Фильтрация по температуре (показать выше порога)"""
    global current_filter_temp
    temp_str = filter_temp_entry.get().strip()
    if temp_str:
        if not validate_temperature(temp_str):
            status_label.config(text="Ошибка: Температура фильтра должна быть числом!", fg="red")
            return
        current_filter_temp = float(temp_str)
    else:
        current_filter_temp = None
    
    refresh_table(table_frame)
    
    if current_filter_temp is not None:
        status_label.config(text=f"Фильтр: температура > {current_filter_temp}°C", fg="blue")
    else:
        status_label.config(text="Фильтр по температуре сброшен", fg="blue")

def reset_filters(filter_date_entry, filter_temp_entry, table_frame):
    """Сброс всех фильтров"""
    global current_filter_date, current_filter_temp
    current_filter_date = ""
    current_filter_temp = None
    filter_date_entry.delete(0, tk.END)
    filter_temp_entry.delete(0, tk.END)
    refresh_table(table_frame)
    status_label.config(text="Фильтры сброшены", fg="blue")

def delete_record(table_frame):
    """Удаление выбранной записи"""
    selection_window = tk.Toplevel()
    selection_window.title("Удаление записи о погоде")
    selection_window.geometry("500x350")
    
    tk.Label(selection_window, text="Выберите запись для удаления:", font=("Arial", 10, "bold")).pack(pady=10)
    
    listbox = tk.Listbox(selection_window, width=60)
    listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    # Заполнение списка
    for i, rec in enumerate(records):
        precip = "Да" if rec.get("precipitation", False) else "Нет"
        listbox.insert(tk.END, f"{i+1}. {rec['date']} | {rec['temperature']}°C | {rec['description']} | Осадки: {precip}")
    
    def delete_selected():
        selected = listbox.curselection()
        if selected:
            index = selected[0]
            deleted_rec = records.pop(index)
            save_data()
            refresh_table(table_frame)
            selection_window.destroy()
            status_label.config(text=f"Запись за {deleted_rec['date']} удалена!", fg="red")
        else:
            status_label.config(text="Ошибка: Выберите запись для удаления!", fg="red")
    
    tk.Button(selection_window, text="Удалить", command=delete_selected, bg="red", fg="white").pack(pady=10)

def main():
    global status_label
    
    root = tk.Tk()
    root.title("Weather Diary - Дневник погоды")
    root.geometry("900x600")
    root.configure(bg="#f0f0f0")
    
    # Загрузка данных
    load_data()
    
    # Фрейм для ввода данных
    input_frame = tk.Frame(root, bg="#f0f0f0", bd=2, relief="groove")
    input_frame.pack(fill="x", padx=10, pady=10)
    
    tk.Label(input_frame, text="ДОБАВЛЕНИЕ ЗАПИСИ О ПОГОДЕ", font=("Arial", 12, "bold"), bg="#f0f0f0").grid(row=0, column=0, columnspan=4, pady=5)
    
    tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    date_entry = tk.Entry(input_frame, width=15)
    date_entry.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(input_frame, text="Температура (°C):", bg="#f0f0f0").grid(row=1, column=2, padx=5, pady=5, sticky="e")
    temp_entry = tk.Entry(input_frame, width=10)
    temp_entry.grid(row=1, column=3, padx=5, pady=5)
    
    tk.Label(input_frame, text="Описание:", bg="#f0f0f0").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    desc_entry = tk.Entry(input_frame, width=40)
    desc_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="w")
    
    # Чекбокс для осадков
    precip_var = tk.BooleanVar()
    precip_check = tk.Checkbutton(input_frame, text="Осадки", variable=precip_var, bg="#f0f0f0")
    precip_check.grid(row=2, column=3, padx=5, pady=5, sticky="w")
    
    # Кнопки добавления и удаления
    button_frame = tk.Frame(root, bg="#f0f0f0")
    button_frame.pack(fill="x", padx=10, pady=5)
    
    add_button = tk.Button(button_frame, text="ДОБАВИТЬ ЗАПИСЬ", bg="green", fg="white", font=("Arial", 10, "bold"),
                          command=lambda: add_record(date_entry, temp_entry, desc_entry, precip_var, table_frame))
    add_button.pack(side="left", padx=5)
    
    delete_button = tk.Button(button_frame, text="УДАЛИТЬ ЗАПИСЬ", bg="red", fg="white", font=("Arial", 10, "bold"),
                            command=lambda: delete_record(table_frame))
    delete_button.pack(side="left", padx=5)
    
    # Фрейм для фильтрации
    filter_frame = tk.Frame(root, bg="#f0f0f0", bd=2, relief="groove")
    filter_frame.pack(fill="x", padx=10, pady=10)
    
    tk.Label(filter_frame, text="ФИЛЬТРАЦИЯ", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=0, column=0, columnspan=4, pady=5)
    
    tk.Label(filter_frame, text="По дате:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    filter_date_entry = tk.Entry(filter_frame, width=15)
    filter_date_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Button(filter_frame, text="Применить", command=lambda: filter_by_date(filter_date_entry, table_frame)).grid(row=1, column=2, padx=5)
    
    tk.Label(filter_frame, text="Температура >", bg="#f0f0f0").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    filter_temp_entry = tk.Entry(filter_frame, width=10)
    filter_temp_entry.grid(row=2, column=1, padx=5, pady=5)
    tk.Button(filter_frame, text="Применить", command=lambda: filter_by_temp(filter_temp_entry, table_frame)).grid(row=2, column=2, padx=5)
    
    tk.Button(filter_frame, text="СБРОСИТЬ ФИЛЬТРЫ", bg="orange", 
              command=lambda: reset_filters(filter_date_entry, filter_temp_entry, table_frame)).grid(row=1, column=3, rowspan=2, padx=20)
    
    # Статус бар
    status_label = tk.Label(root, text="Готов к работе", relief="sunken", anchor="w", bg="#ffffcc")
    status_label.pack(fill="x", side="bottom", padx=10, pady=5)
    
    # Фрейм для таблицы
    table_frame = tk.Frame(root, bg="white")
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Отображение записей
    display_records(table_frame, records)
    
    root.mainloop()

if __name__ == "__main__":
    main()
