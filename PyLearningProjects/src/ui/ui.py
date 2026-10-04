""" =========================================================
        Графический интерфейс на Tkinter
    =========================================================
"""

import tkinter as tk
from tkinter import messagebox
from config import NAME_FILE_SAVES
from storage import load_collection, save_collection
from utils import ensure_save_file


listbox = None
entry_task = None
name_file = NAME_FILE_SAVES
collection = []


def refresh_list():
    listbox.delete(0, tk.END)
    for task in collection:
        listbox.insert(tk.END, task)


def on_add():
    text = entry_task.get().strip()
    if not text:
        messagebox.showwarning("Внимание", "Введите текст задачи")
        return
    if text in collection:
        messagebox.showwarning("Внимание", "Такая задача уже есть")
        return
    collection.append(text)
    save_collection(collection, name_file)
    refresh_list()
    entry_task.delete(0, tk.END)


def on_edit():
    pass


def on_delete():
    pass


def build_ui(root):
    global collection
    global entry_task, listbox

    collection = load_collection([], name_file)

    # Верхняя панель: поле ввода + кнопка "Добавить"
    frame_top = tk.Frame(root, pady=5)
    frame_top.pack(fill="x", padx=10)

    tk.Label(frame_top, text="Задача:").pack(side="left")
    entry_task = tk.Entry(frame_top)
    entry_task.pack(side="left", fill="x", expand=True, padx=5)
    tk.Button(frame_top, text="Добавить", command=on_add).pack(side="left")

    # Середина: список задач со скроллом
    frame_list = tk.Frame(root)
    frame_list.pack(fill="both", expand=True, padx=10, pady=5)

    scroll = tk.Scrollbar(frame_list)
    scroll.pack(side="right", fill="y")

    listbox = tk.Listbox(frame_list, yscrollcommand=scroll.set)
    listbox.pack(side="left", fill="both", expand=True)
    scroll.config(command=listbox.yview)

    # Нижняя панель: кнопки управления
    frame_bottom = tk.Frame(root, pady=5)
    frame_bottom.pack(fill="x", padx=10)

    tk.Button(frame_bottom, text="Редактировать", command=on_edit).pack(side="left", padx=2)
    tk.Button(frame_bottom, text="Удалить", command=on_delete).pack(side="left", padx=2)
    tk.Button(frame_bottom, text="Выход", command=root.quit).pack(side="right", padx=2)


def main_menu():

    ensure_save_file()
    root = tk.Tk()
    root.title("Task Manager")
    root.geometry("500x400")

    build_ui(root)
    refresh_list()

    root.mainloop()


if __name__ == "__main__":
    main_menu()
