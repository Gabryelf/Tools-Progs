""" =========================================================
        Модуль для отображения задач и выводов
    =========================================================
"""

"""1. выводит список в консоль"""


def show_collection(task_list):
    print("=" * 30)
    for i, j in enumerate(task_list):
        print(i + 1, j)
    print("=" * 30)


"""2. показывает список и ждёт завершение"""


def show_message(message=None, mess_action=None):
    if message is not None:
        print(f"задача {message} успешно {mess_action}")
    input("нажмите любую кнопу для продолжени")
