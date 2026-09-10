"""Weather Notes — блокнот наблюдений о погоде.

Второе приложение проекта Weather Diary.
Позволяет быстро записывать короткие заметки о погоде
с привязкой к дате. Заметки хранятся в notes.json.
"""
import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

NOTES_FILE = "notes.json"


def load_notes():
    if not os.path.exists(NOTES_FILE):
        return []
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_notes(notes):
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Notes — заметки о погоде")
        self.root.geometry("700x500")
        self.notes = load_notes()

        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(self.input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5)
        self.date_entry = tk.Entry(self.input_frame, width=14)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.input_frame, text="Заметка:").grid(row=0, column=2, padx=5)
        self.note_entry = tk.Entry(self.input_frame, width=40)
        self.note_entry.grid(row=0, column=3, padx=5)
        self.note_entry.bind("<Return>", lambda e: self.add_note())

        tk.Button(self.input_frame, text="Добавить", bg="green", fg="white",
                  command=self.add_note).grid(row=0, column=4, padx=5)

        self.listbox = tk.Listbox(root, width=100, height=18)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(btn_frame, text="Удалить заметку", bg="red", fg="white",
                  command=self.delete_note).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Очистить всё", bg="orange",
                  command=self.clear_all).pack(side="left", padx=5)

        self.status = tk.Label(root, text="Готово", anchor="w", relief="sunken")
        self.status.pack(fill="x", side="bottom")

        self.refresh()

    def add_note(self):
        date = self.date_entry.get().strip()
        text = self.note_entry.get().strip()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            self.status.config(text="Неверный формат даты!", fg="red")
            return
        if not text:
            self.status.config(text="Заметка не может быть пустой!", fg="red")
            return
        self.notes.append({"date": date, "text": text})
        save_notes(self.notes)
        self.note_entry.delete(0, tk.END)
        self.status.config(text="Заметка добавлена", fg="green")
        self.refresh()

    def delete_note(self):
        sel = self.listbox.curselection()
        if not sel:
            self.status.config(text="Выберите заметку", fg="red")
            return
        self.notes.pop(sel[0])
        save_notes(self.notes)
        self.refresh()
        self.status.config(text="Заметка удалена", fg="red")

    def clear_all(self):
        if messagebox.askyesno("Подтверждение", "Удалить все заметки?"):
            self.notes = []
            save_notes(self.notes)
            self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for i, n in enumerate(self.notes, 1):
            self.listbox.insert(tk.END, f"{i}. [{n['date']}] {n['text']}")


def main():
    root = tk.Tk()
    NotesApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()