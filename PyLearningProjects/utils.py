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


def get_base_dir():
    """Папка, где лежит EXE (или .py при разработке)."""
    if getattr(sys, 'frozen', False):
        # Запущено из EXE
        return os.path.dirname(sys.executable)
    else:
        # Запущено как обычный .py
        return os.path.dirname(os.path.abspath(__file__))


def ensure_save_file():
    """Если файла нет — создаёт с дефолтным содержимым."""
    if not os.path.exists(config.NAME_FILE_SAVES):
        with open(config.NAME_FILE_SAVES, "w", encoding="utf-8") as f:
            return config.NAME_FILE_SAVES
