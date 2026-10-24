""" =========================================================
        Бизнес-сценарии GUI. Использует Interface.
        Никаких прямых обращений к Tkinter.
    =========================================================
"""
from ui.Interface import Interface
from storage import load_collection, save_collection
from utils import get_base_dir, ensure_save_file


# ---------- состояние приложения ----------
ui = Interface("Task Manager", width=400, height=400)
get_base_dir()
ensure_save_file()
collection = load_collection()


def show_menu():
    ui.clear()
    ui.add_label("Меню", font=("Arial", 16, "bold"))
    ui.add_button("Посмотреть задачи", command=show_all_tasks)
    ui.add_button("Добавить задачу", command=show_add)
    ui.add_button("Выход", command=ui.quit, bg="red")


def show_all_tasks():
    ui.clear()
    ui.add_label(f"Задач: {len(collection)}", font=("Arial", 14, "bold"))

    listbox = ui.add_listbox()
    for index, task in enumerate(collection):
        listbox.insert("end", f"{index + 1}. {task['name']}")

    ui.add_button("В меню", command=show_menu)


def show_add():
    ui.clear()
    ui.add_label("Новая задача", font=("Arial", 14, "bold"))

    ui.add_label("Имя:")
    entry_name = ui.add_entry()

    ui.add_label("Содержание:")
    text_desc = ui.add_text()

    def do_add():
        name = entry_name.get().strip()
        desc = text_desc.get("1.0", "end").strip()
        if not name:
            ui.show_warning("Внимание", "Имя не может быть пустым")
            return
        collection.append({"name": name, "content": desc})
        save_collection(collection)
        show_all_tasks()

    ui.add_button("Сохранить", command=do_add)
    ui.add_button("В меню", command=show_menu)


def run():
    show_menu()
    ui.run()
