"""Точка входа в приложение"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from src.core.overlay_window import OverlayWindow
from src.ui.control_panel import ControlPanel
from src.utils.constants import APP_NAME

def resource_path(relative_path):
    """Получить путь к ресурсам для exe файла"""
    try:
        # PyInstaller создает временную папку и сохраняет путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Application:
    def __init__(self):
        # Устанавливаем атрибут для работы с ресурсами
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName(APP_NAME)

        # Создаем оверлей
        self.overlay = OverlayWindow()
        # Создаем панель управления
        self.panel = ControlPanel(self.overlay)
        self.panel.show()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app = Application()
    app.run()
