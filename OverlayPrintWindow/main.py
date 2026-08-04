# ================================================================================
# Main Application - active point - точка входа в главное приложение
# ================================================================================


import sys
from PyQt5.QtWidgets import QApplication

from src.core.overlay_window import OverlayWindow
from src.services.controls import Controller
from src.ui.menu_manager import GuiManager


class Main:
    def __init__(self):
        # Создаем приложение Qt
        self.app = QApplication(sys.argv)

        # Создаем окно
        self.window = OverlayWindow()

        # Создаем менеджер UI
        self.gui = GuiManager()

        # Создаем контроллер и передаем ему ссылку на окно
        self.controller = Controller(self.window)

        # Передаем контроллер в окно
        self.window.set_controller(self.controller)

        # Выводим подсказки в консоль
        self.print_help()

        # Запускаем цикл обработки событий
        sys.exit(self.app.exec_())

    def print_help(self):
        self.gui.show_start_menu()


if __name__ == "__main__":
    main_app = Main()
