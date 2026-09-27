""" =========================================================
        Модуль для дополнительных функций приложения
    =========================================================
"""

"""подтверждение действия"""


def check_confirm(action: str):
    confirm = input("точно?"
                    "\n Y/N")
    if (confirm.capitalize().startswith('') == "Y"
            or 'Д'):
        print(action)
        return False
    else:
        print("отмена")
        return True
