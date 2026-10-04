""" =========================================================
        Модуль для основного цикла приложения
    =========================================================
"""


import config
from utils import check_confirm, ensure_save_file
from core import create_task, edited_task, deleated_task
from storage import save_collection, load_collection
from ui.view import show_collection, show_message

"""основной цикл приложения"""


def app():
    ensure_save_file()
    name_file = config.NAME_FILE_SAVES
    collection = load_collection([], name_file)
    is_running = True

    while is_running:
        print('1 - посмотреть задачи'
              '\n2 - добавить задачу'
              '\n3 - редактирование'
              '\n4 - снять задачу'
              '\n5 - выход')
        choice_user = input("введите команду: ")

        match choice_user:
            case "1":  # просмотр списка
                show_collection(collection)
            case "2":  # добавление в список
                create_task(collection, name_file)
            case "3":  # изменение элемента
                edited_task(collection)
                save_collection(collection, name_file)
            case "4":  # удаление элемента
                show_collection(collection)
                deleated_task(collection)
                save_collection(collection, name_file)
            case "5":  # завершение цикла
                is_running = check_confirm('отключение...')
            case _:  # неверная команда
                print('неверная команда')
                show_message()

