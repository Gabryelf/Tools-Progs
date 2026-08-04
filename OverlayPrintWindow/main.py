import sys
from PyQt5.QtWidgets import QApplication

from src.core.overlay_window import OverlayWindow
from src.services.controls import Controller
from src.ui.menu_manager import GuiManager


class Main:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = OverlayWindow()
        self.gui = GuiManager()
        self.controller = Controller(self.window)
        self.window.set_controller(self.controller)
        self.gui.show_start_menu()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    main_app = Main()