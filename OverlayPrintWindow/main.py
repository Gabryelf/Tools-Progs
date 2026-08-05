"""Точка входа в приложение"""
import sys
from PyQt5.QtWidgets import QApplication
from src.core.overlay_window import OverlayWindow
from src.ui.control_panel import ControlPanel
from src.utils.constants import APP_NAME

class Application:
    def __init__(self):
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