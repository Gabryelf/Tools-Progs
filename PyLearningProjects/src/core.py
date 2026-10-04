""" =============================================================
        Модуль для основных функциональных методов приложения
    =============================================================
"""

from ui.view import show_message, show_collection
from storage import save_collection
from utils import check_confirm

"""содзание задач"""


def create_task(task_list, file):
    name_task = input("введите имя задачи")
    if len(name_task) > 0 and name_task not in task_list and name_task is not None:
        content_task = input("введите описание задачи")
        if content_task is not None and len(content_task) >= 1:
            full_task = f"{name_task} {content_task}"
            task_list.append(full_task)
            save_collection(task_list, file_name=file)
            show_message(message=name_task, mess_action='добавлена')


"""изменение задачи"""


def edited_task(task_list):
    show_collection(task_list)
    select_edit = int(input('введите номер задачи: '))
    edit_name = input("новое имя задачи: ")
    task_list[select_edit - 1] = edit_name
    show_message(message=edit_name, mess_action='измененна')


"""удаление элемента"""


def deleated_task(task_list):
    delete_edit = int(input('введите номер задачи: '))
    if not check_confirm('удаление выполненно'):
        task_list.pop(delete_edit - 1)
    show_collection(task_list)
    show_message(message=delete_edit, mess_action="удалена")