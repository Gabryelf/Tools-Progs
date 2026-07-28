# screen_recorder/main.py
"""
Точка входа в приложение
"""

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Главная функция"""
    app = QApplication(sys.argv)
    app.setApplicationName("Screen Recorder")
    app.setApplicationVersion("0.0.2")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
