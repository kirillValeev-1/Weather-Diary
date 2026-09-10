"""
Weather Diary — дневник погоды.
Главный модуль приложения (GUI на tkinter).
"""
import tkinter as tk
from tkinter import filedialog, messagebox

from models import WeatherRecord
from storage import load_records, save_records
from validators import validate_date, validate_temperature, validate_record
from statistics import summary
from exporters import export_to_csv, import_from_csv
from themes import get_theme


records = []
current_filter_date = ""
current_filter_temp = None
current_search = ""
date_from = ""
date_to = ""
only_precipitation = False
status_label = None
sort_column = None
sort_reverse = False
current_theme = "light"


def load_data() -> None:
    global records
    records = load_records()


def save_data() -> None:
    save_records(records)


def clear_table(table_frame: tk.Frame) -> None:
    for widget in table_frame.winfo_children():
        widget.destroy()


def sort_by(column, table_frame) -> None:
    global records, sort_column, sort_reverse
    if sort_column == column:
        sort_reverse = not sort_reverse
    else:
        sort_column = column
        sort_reverse = False
    key_map = {
        "date": lambda r: r.date,
        "temperature": lambda r: r.temperature,
        "description": lambda r: r.description.lower(),
        "precipitation": lambda r: r.precipitation,
    }
    records.sort(key=key_map[column], reverse=sort_reverse)
    save_data()
    refresh_table(table_frame)
    status_label.config(
        text=f"Сортировка по '{column}' ({'убыв.' if sort_reverse else 'возр.'})",
        fg="blue")


def display_records(table_frame: tk.Frame, record_list: list) -> None:
    clear_table(table_frame)
    headers = [("Дата", "date"), ("", None), ("Температура", "temperature"),
               ("Описание", "description"), ("Осадки", "precipitation")]
    for col, (header, key) in enumerate(headers):
        lbl = tk.Label(table_frame, text=header, font=("Arial", 10, "bold"),
                       borderwidth=1, relief="solid", padx=10, pady=5,
                       bg="lightgray",
                       cursor="hand2" if key else "arrow")
        lbl.grid(row=0, column=col, sticky="nsew")
        if key:
            lbl.bind("<Button-1>", lambda e, k=key: sort_by(k, table_frame))

    for row, rec in enumerate(record_list, start=1):
        tk.Label(table_frame, text=rec.date,
                 borderwidth=1, relief="solid", padx=10, pady=5
                 ).grid(row=row, column=0, sticky="nsew")
        tk.Label(table_frame, text=rec.weather_emoji(),
                 borderwidth=1, relief="solid", padx=10, pady=5,
                 font=("Arial", 12)
                 ).grid(row=row, column=1, sticky="nsew")
        tk.Label(table_frame, text=str(rec.temperature),
                 borderwidth=1, relief="solid", padx=10, pady=5
                 ).grid(row=row, column=2, sticky="nsew")
        tk.Label(table_frame, text=rec.description,
                 borderwidth=1, relief="solid", padx=10, pady=5
                 ).grid(row=row, column=3, sticky="nsew")
        tk.Label(table_frame, text=rec.precip_text(),
                 borderwidth=1, relief="solid", padx=10, pady=5
                 ).grid(row=row, column=4, sticky="nsew")
    for col in range(5):
        table_frame.columnconfigure(col, weight=1)


def refresh_table(table_frame: tk.Frame) -> None:
    filtered = filter_records()
    display_records(table_frame, filtered)
    stats_label.config(text=summary(filtered))


def filter_records() -> list:
    global current_filter_date, current_filter_temp, current_search
    global date_from, date_to, only_precipitation
    filtered = records.copy()
    if current_filter_date:
        filtered = [r for r in filtered if r.date == current_filter_date]
    if current_filter_temp is not None:
        filtered = [r for r in filtered if r.temperature > current_filter_temp]
    if current_search:
        filtered = [r for r in filtered if current_search in r.description.lower()]
    if date_from:
        filtered = [r for r in filtered if r.date >= date_from]
    if date_to:
        filtered = [r for r in filtered if r.date <= date_to]
    if only_precipitation:
        filtered = [r for r in filtered if r.precipitation]
    return filtered


def add_record(date_entry, temp_entry, desc_entry, precip_var, table_frame) -> None:
    date = date_entry.get().strip()
    temp = temp_entry.get().strip()
    desc = desc_entry.get().strip()
    precipitation = precip_var.get()
    ok, err = validate_record(date, temp, desc)
    if not ok:
        status_label.config(text=f"Ошибка: {err}", fg="red")
        return
    records.append(WeatherRecord(date=date, temperature=float(temp),
                                 description=desc, precipitation=precipitation))
    save_data()
    date_entry.delete(0, tk.END)
    temp_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)
    precip_var.set(False)
    status_label.config(text=f"Запись за {date} добавлена!", fg="green")
    refresh_table(table_frame)


def edit_record(table_frame) -> None:
    if not records:
        status_label.config(text="Нет записей для редактирования", fg="red")
        return
    win = tk.Toplevel()
    win.title("Редактирование записи")
    win.geometry("500x350")
    tk.Label(win, text="Выберите запись:").pack(pady=5)
    listbox = tk.Listbox(win, width=70, height=8)
    listbox.pack(fill="both", expand=True, padx=10)
    for i, rec in enumerate(records):
        listbox.insert(tk.END,
                       f"{i+1}. {rec.date} | {rec.temperature}°C | {rec.description}")

    def apply_edit():
        sel = listbox.curselection()
        if not sel:
            return
        rec = records[sel[0]]
        edit_win = tk.Toplevel(win)
        edit_win.title("Новые данные")
        edit_win.geometry("380x240")
        tk.Label(edit_win, text="Дата:").grid(row=0, column=0, padx=5, pady=5)
        e_date = tk.Entry(edit_win); e_date.insert(0, rec.date)
        e_date.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(edit_win, text="Температура:").grid(row=1, column=0, padx=5, pady=5)
        e_temp = tk.Entry(edit_win); e_temp.insert(0, str(rec.temperature))
        e_temp.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(edit_win, text="Описание:").grid(row=2, column=0, padx=5, pady=5)
        e_desc = tk.Entry(edit_win, width=30); e_desc.insert(0, rec.description)
        e_desc.grid(row=2, column=1, padx=5, pady=5)
        p_var = tk.BooleanVar(value=rec.precipitation)
        tk.Checkbutton(edit_win, text="Осадки", variable=p_var
                       ).grid(row=3, column=1, pady=5)

        def save_changes():
            ok, err = validate_record(e_date.get(), e_temp.get(), e_desc.get())
            if not ok:
                status_label.config(text=f"Ошибка: {err}", fg="red")
                return
            rec.date = e_date.get().strip()
            rec.temperature = float(e_temp.get())
            rec.description = e_desc.get().strip()
            rec.precipitation = p_var.get()
            save_data()
            refresh_table(table_frame)
            edit_win.destroy()
            win.destroy()
            status_label.config(text="Запись обновлена", fg="green")

        tk.Button(edit_win, text="Сохранить", command=save_changes,
                  bg="green", fg="white").grid(row=4, column=0, columnspan=2, pady=10)

    tk.Button(win, text="Редактировать", command=apply_edit,
              bg="blue", fg="white").pack(pady=10)


def filter_by_date(filter_date_entry, table_frame) -> None:
    global current_filter_date
    date_str = filter_date_entry.get().strip()
    if date_str and not validate_date(date_str):
        status_label.config(text="Ошибка: Неверный формат даты для фильтра!", fg="red")
        return
    current_filter_date = date_str
    refresh_table(table_frame)
    status_label.config(
        text=f"Фильтр по дате: {current_filter_date}" if current_filter_date
        else "Фильтр по дате сброшен", fg="blue")


def filter_by_temp(filter_temp_entry, table_frame) -> None:
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
    status_label.config(
        text=f"Фильтр: температура > {current_filter_temp}°C" if current_filter_temp is not None
        else "Фильтр по температуре сброшен", fg="blue")


def search_records(query, table_frame) -> None:
    global current_search
    current_search = query.strip().lower()
    refresh_table(table_frame)
    status_label.config(
        text=f"Поиск: '{current_search}'" if current_search else "Поиск сброшен",
        fg="blue")


def filter_by_range(from_entry, to_entry, table_frame) -> None:
    global date_from, date_to
    d1 = from_entry.get().strip()
    d2 = to_entry.get().strip()
    if d1 and not validate_date(d1):
        status_label.config(text="Ошибка: неверная начальная дата", fg="red")
        return
    if d2 and not validate_date(d2):
        status_label.config(text="Ошибка: неверная конечная дата", fg="red")
        return
    date_from, date_to = d1, d2
    refresh_table(table_frame)
    status_label.config(text=f"Диапазон: {d1 or '...'} — {d2 or '...'}", fg="blue")


def toggle_precip_filter(var, table_frame) -> None:
    global only_precipitation
    only_precipitation = var.get()
    refresh_table(table_frame)
    status_label.config(
        text=f"Осадки: {'только с осадками' if only_precipitation else 'все'}",
        fg="blue")


def reset_filters(filter_date_entry, filter_temp_entry, search_entry,
                  range_from, range_to, precip_var, table_frame) -> None:
    global current_filter_date, current_filter_temp, current_search
    global date_from, date_to, only_precipitation
    current_filter_date = ""
    current_filter_temp = None
    current_search = ""
    date_from = ""
    date_to = ""
    only_precipitation = False
    precip_var.set(False)
    filter_date_entry.delete(0, tk.END)
    filter_temp_entry.delete(0, tk.END)
    search_entry.delete(0, tk.END)
    range_from.delete(0, tk.END)
    range_to.delete(0, tk.END)
    refresh_table(table_frame)
    status_label.config(text="Фильтры сброшены", fg="blue")


def do_export(table_frame) -> None:
    rows = filter_records()
    if not rows:
        status_label.config(text="Нечего экспортировать", fg="red")
        return
    if export_to_csv(rows):
        status_label.config(text="Экспорт в weather_export.csv выполнен", fg="green")
    else:
        status_label.config(text="Ошибка экспорта", fg="red")


def do_import(table_frame) -> None:
    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not path:
        return
    imported = import_from_csv(path)
    if not imported:
        status_label.config(text="Не удалось импортировать записи", fg="red")
        return
    records.extend(imported)
    save_data()
    refresh_table(table_frame)
    status_label.config(text=f"Импортировано записей: {len(imported)}", fg="green")


def apply_theme(root, theme_name, table_frame) -> None:
    """Применяет цветовую тему ко всем виджетам."""
    global current_theme
    current_theme = theme_name
    theme = get_theme(theme_name)

    def walk(widget):
        try:
            widget.configure(bg=theme["bg"])
        except tk.TclError:
            pass
        if isinstance(widget, tk.Label):
            try:
                widget.configure(fg=theme["fg"])
            except tk.TclError:
                pass
        for child in widget.winfo_children():
            walk(child)

    root.configure(bg=theme["bg"])
    walk(root)
    table_frame.configure(bg=theme["table_bg"])
    refresh_table(table_frame)


def toggle_theme(root, table_frame) -> None:
    """Переключает светлую/тёмную тему."""
    new_theme = "dark" if current_theme == "light" else "light"
    apply_theme(root, new_theme, table_frame)
    status_label.config(text=f"Тема: {new_theme}", fg="blue")


def delete_record(table_frame) -> None:
    selection_window = tk.Toplevel()
    selection_window.title("Удаление записи о погоде")
    selection_window.geometry("500x350")
    tk.Label(selection_window, text="Выберите запись для удаления:",
             font=("Arial", 10, "bold")).pack(pady=10)
    listbox = tk.Listbox(selection_window, width=60)
    listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    for i, rec in enumerate(records):
        listbox.insert(tk.END,
                       f"{i+1}. {rec.date} | {rec.temperature}°C | "
                       f"{rec.description} | Осадки: {rec.precip_text()}")

    def delete_selected():
        selected = listbox.curselection()
        if not selected:
            status_label.config(text="Ошибка: Выберите запись для удаления!", fg="red")
            return
        deleted_rec = records.pop(selected[0])
        save_data()
        refresh_table(table_frame)
        selection_window.destroy()
        status_label.config(text=f"Запись за {deleted_rec.date} удалена!", fg="red")

    tk.Button(selection_window, text="Удалить",
              command=delete_selected, bg="red", fg="white").pack(pady=10)


def main() -> None:
    global status_label

    root = tk.Tk()
    root.title("Weather Diary - Дневник погоды")
    root.geometry("1000x820")
    root.configure(bg="#f0f0f0")

    load_data()

    input_frame = tk.Frame(root, bg="#f0f0f0", bd=2, relief="groove")
    input_frame.pack(fill="x", padx=10, pady=10)
    tk.Label(input_frame, text="ДОБАВЛЕНИЕ ЗАПИСИ О ПОГОДЕ",
             font=("Arial", 12, "bold"), bg="#f0f0f0"
             ).grid(row=0, column=0, columnspan=4, pady=5)
    tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):", bg="#f0f0f0"
             ).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    date_entry = tk.Entry(input_frame, width=15)
    date_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Label(input_frame, text="Температура (°C):", bg="#f0f0f0"
             ).grid(row=1, column=2, padx=5, pady=5, sticky="e")
    temp_entry = tk.Entry(input_frame, width=10)
    temp_entry.grid(row=1, column=3, padx=5, pady=5)
    tk.Label(input_frame, text="Описание:", bg="#f0f0f0"
             ).grid(row=2, column=0, padx=5, pady=5, sticky="e")
    desc_entry = tk.Entry(input_frame, width=40)
    desc_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="w")
    precip_var = tk.BooleanVar()
    tk.Checkbutton(input_frame, text="Осадки", variable=precip_var, bg="#f0f0f0"
                   ).grid(row=2, column=3, padx=5, pady=5, sticky="w")

    button_frame = tk.Frame(root, bg="#f0f0f0")
    button_frame.pack(fill="x", padx=10, pady=5)
    tk.Button(button_frame, text="ДОБАВИТЬ", bg="green", fg="white",
              font=("Arial", 10, "bold"),
              command=lambda: add_record(date_entry, temp_entry, desc_entry,
                                         precip_var, table_frame)
              ).pack(side="left", padx=5)
    tk.Button(button_frame, text="РЕДАКТИРОВАТЬ", bg="blue", fg="white",
              font=("Arial", 10, "bold"),
              command=lambda: edit_record(table_frame)
              ).pack(side="left", padx=5)
    tk.Button(button_frame, text="УДАЛИТЬ", bg="red", fg="white",
              font=("Arial", 10, "bold"),
              command=lambda: delete_record(table_frame)
              ).pack(side="left", padx=5)
    tk.Button(button_frame, text="ЭКСПОРТ В CSV", bg="#4a90d9", fg="white",
              font=("Arial", 10, "bold"),
              command=lambda: do_export(table_frame)
              ).pack(side="left", padx=5)
    tk.Button(button_frame, text="ИМПОРТ ИЗ CSV", bg="#4a90d9", fg="white",
              font=("Arial", 10, "bold"),
              command=lambda: do_import(table_frame)
              ).pack(side="left", padx=5)
    tk.Button(button_frame, text="СМЕНИТЬ ТЕМУ", bg="#666", fg="white",
              font=("Arial", 10, "bold"),
              command=lambda: toggle_theme(root, table_frame)
              ).pack(side="left", padx=5)

    filter_frame = tk.Frame(root, bg="#f0f0f0", bd=2, relief="groove")
    filter_frame.pack(fill="x", padx=10, pady=10)
    tk.Label(filter_frame, text="ФИЛЬТРАЦИЯ И ПОИСК",
             font=("Arial", 10, "bold"), bg="#f0f0f0"
             ).grid(row=0, column=0, columnspan=4, pady=5)

    tk.Label(filter_frame, text="По дате:", bg="#f0f0f0"
             ).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    filter_date_entry = tk.Entry(filter_frame, width=15)
    filter_date_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Button(filter_frame, text="Применить",
              command=lambda: filter_by_date(filter_date_entry, table_frame)
              ).grid(row=1, column=2, padx=5)

    tk.Label(filter_frame, text="Температура >", bg="#f0f0f0"
             ).grid(row=2, column=0, padx=5, pady=5, sticky="e")
    filter_temp_entry = tk.Entry(filter_frame, width=10)
    filter_temp_entry.grid(row=2, column=1, padx=5, pady=5)
    tk.Button(filter_frame, text="Применить",
              command=lambda: filter_by_temp(filter_temp_entry, table_frame)
              ).grid(row=2, column=2, padx=5)

    tk.Label(filter_frame, text="Поиск:", bg="#f0f0f0"
             ).grid(row=3, column=0, padx=5, pady=5, sticky="e")
    search_entry = tk.Entry(filter_frame, width=20)
    search_entry.grid(row=3, column=1, padx=5, pady=5)
    tk.Button(filter_frame, text="Найти",
              command=lambda: search_records(search_entry.get(), table_frame)
              ).grid(row=3, column=2, padx=5)

    tk.Label(filter_frame, text="С даты:", bg="#f0f0f0"
             ).grid(row=4, column=0, padx=5, pady=5, sticky="e")
    range_from = tk.Entry(filter_frame, width=12)
    range_from.grid(row=4, column=1, padx=5, pady=5, sticky="w")
    tk.Label(filter_frame, text="По:", bg="#f0f0f0"
             ).grid(row=4, column=1, padx=5, pady=5, sticky="e")
    range_to = tk.Entry(filter_frame, width=12)
    range_to.grid(row=4, column=2, padx=5, pady=5, sticky="w")
    tk.Button(filter_frame, text="Применить диапазон",
              command=lambda: filter_by_range(range_from, range_to, table_frame)
              ).grid(row=4, column=3, padx=5)

    precip_filter_var = tk.BooleanVar()
    tk.Checkbutton(filter_frame, text="Только с осадками",
                   variable=precip_filter_var, bg="#f0f0f0",
                   command=lambda: toggle_precip_filter(precip_filter_var, table_frame)
                   ).grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    tk.Button(filter_frame, text="СБРОСИТЬ ВСЁ", bg="orange",
              command=lambda: reset_filters(filter_date_entry, filter_temp_entry,
                                            search_entry, range_from, range_to,
                                            precip_filter_var, table_frame)
              ).grid(row=1, column=3, rowspan=5, padx=20)

    status_label = tk.Label(root, text="Готов к работе", relief="sunken",
                            anchor="w", bg="#ffffcc")
    status_label.pack(fill="x", side="bottom", padx=10, pady=5)

    table_frame = tk.Frame(root, bg="white")
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    stats_frame = tk.Frame(root, bg="#e0e8f0", bd=2, relief="groove")
    stats_frame.pack(fill="x", padx=10, pady=5)
    stats_label = tk.Label(stats_frame, text=summary(records),
                           font=("Arial", 10), bg="#e0e8f0")
    stats_label.pack(pady=5)

    display_records(table_frame, records)
    stats_label.config(text=summary(records))

    root.mainloop()


if __name__ == "__main__":
    main()