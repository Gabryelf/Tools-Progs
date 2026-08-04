from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class Controller:
    def __init__(self, window):
        self.window = window

    def handle_key_press(self, event):
        """Обработка нажатий клавиш"""
        key = event.key()
        modifiers = event.modifiers()

        # Выход
        if key == Qt.Key_Escape:
            if self.window.is_drawing_mode:
                self.window.toggle_drawing_mode()
            else:
                self.window.close()

        # Справка
        elif key == Qt.Key_F1:
            self.window.show_help()

        # Включить/выключить режим рисования
        elif key == Qt.Key_F2:
            self.window.toggle_drawing_mode()

        # Пауза
        elif key == Qt.Key_F3:
            self.window.toggle_pause()

        # Очистка
        elif key == Qt.Key_C:
            self.window.clear_all()

        # Отмена
        elif key == Qt.Key_Z and modifiers & Qt.ControlModifier:
            self.window.undo_last()

        # Цвета
        elif key == Qt.Key_R:
            self.window.change_color(QColor(255, 0, 0, 255), "Красный")
        elif key == Qt.Key_G:
            self.window.change_color(QColor(0, 255, 0, 255), "Зеленый")
        elif key == Qt.Key_B:
            self.window.change_color(QColor(0, 0, 255, 255), "Синий")
        elif key == Qt.Key_Y:
            self.window.change_color(QColor(255, 255, 0, 255), "Желтый")
        elif key == Qt.Key_P:
            self.window.change_color(QColor(255, 0, 255, 255), "Розовый")
        elif key == Qt.Key_O:
            self.window.change_color(QColor(255, 165, 0, 255), "Оранжевый")
        elif key == Qt.Key_W:
            self.window.change_color(QColor(255, 255, 255, 255), "Белый")
        elif key == Qt.Key_1:
            self.window.change_width(3)
        elif key == Qt.Key_2:
            self.window.change_width(5)
        elif key == Qt.Key_3:
            self.window.change_width(10)
        elif key == Qt.Key_4:
            self.window.change_width(15)
        elif key == Qt.Key_5:
            self.window.change_width(25)
