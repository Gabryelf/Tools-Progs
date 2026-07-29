"""
Главный модуль приложения Copy Code Pro
"""
import sys
import os
from pathlib import Path

# Добавляем родительскую папку в путь для импортов
# Так как main.py находится в src, parent = desctop_app
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import tkinter as tk
from src.ui.main_window import MainWindow


def main():
    """Главная функция приложения"""
    try:
        # Создаем корневое окно
        root = tk.Tk()

        # Создаем главное окно
        app = MainWindow(root)

        # Запускаем главный цикл
        root.mainloop()

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")


if __name__ == '__main__':
    main()
