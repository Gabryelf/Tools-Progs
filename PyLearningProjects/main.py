""" Приложение Task Manager
    version 0.0.3
    создает  i/o функционал для ввода заметки
"""

is_running = True
collection = ["создать версию 1", "попить кофе"]
print("Приветствуем вас в приложении  TASK MANAGER")

while is_running:
    print('1 - посмотреть задачи'
          '\n2 - добавить задачу'
          '\n3 - редактировать задачу'
          '\n4 - удалить задачу'
          '\n5 - выход')
    choice_user = input("введите команду: ")

    match choice_user:
        case "1":
            print("-" * 30)
            for key, item in enumerate(collection):
                print(key + 1, item)
            print("-" * 30)
            waite = input("Нажмите 'ENTER' для продолжения")
        case "2":
            task_name = input('введите название задачи: ')
            collection.append(task_name)
        case "3":
            for key, item in enumerate(collection):
                print(key + 1, item)
            select_edit = int(input('введите номер задачи: '))
            edit_name = input("новое имя задачи: ")
            collection[select_edit - 1] = edit_name
        case "4":
            for key, item in enumerate(collection):
                print(key + 1, item)
            delete_edit = int(input('введите номер задачи: '))
            collection.pop(delete_edit - 1)
        case "5":
            print("отключение...")
            is_running = False
        case _:
            print('неверная команда')


