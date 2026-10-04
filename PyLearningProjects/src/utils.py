""" =========================================================
        Модуль для дополнительных функций приложения
    =========================================================
"""

import os
import sys
import config

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


"""Папка, где лежит EXE (или .py при разработке)."""


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


"""Если файла нет — создаёт с дефолтным содержимым."""


def ensure_save_file():
    if not os.path.exists(config.NAME_FILE_SAVES):
        with open(config.NAME_FILE_SAVES, "w", encoding="utf-8"):
            return config.NAME_FILE_SAVES
