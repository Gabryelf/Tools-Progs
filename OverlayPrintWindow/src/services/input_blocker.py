"""Блокировка ввода (для будущих расширений)"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from src.core.drawing_engine import DrawingMode


class Controller:
    def __init__(self, window):
        self.window = window

    def handle_key_press(self, event):
        """Обработка нажатий клавиш"""
        key = event.key()
        modifiers = event.modifiers()

        # Выход
        if key == Qt.Key_Escape:
            if self.window.engine.is_active:
                self.window.toggle_drawing_mode()
            else:
                self.window.close()

        # Справка
        elif key == Qt.Key_F1:
            self.show_help()

        # Режим рисования
        elif key == Qt.Key_F2:
            self.window.toggle_drawing_mode()

        # Затухание
        elif key == Qt.Key_F4:
            self.window.toggle_fading()

        # Режимы рисования
        elif key == Qt.Key_F:
            self.window.set_drawing_mode_type(DrawingMode.FREE)
        elif key == Qt.Key_L:
            self.window.set_drawing_mode_type(DrawingMode.LINE)
        elif key == Qt.Key_R:
            self.window.set_drawing_mode_type(DrawingMode.RECTANGLE)
        elif key == Qt.Key_C:
            self.window.set_drawing_mode_type(DrawingMode.CIRCLE)
        elif key == Qt.Key_T:
            self.window.set_drawing_mode_type(DrawingMode.TRIANGLE)

        # Очистка
        elif key == Qt.Key_Delete:
            self.window.clear_all()

        # Отмена
        elif key == Qt.Key_Z and modifiers & Qt.ControlModifier:
            self.window.undo()

        # Цвета
        elif key in [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4,
                     Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8]:
            colors = [(255, 50, 50), (50, 255, 50), (50, 150, 255),
                      (255, 255, 50), (200, 50, 255), (255, 150, 50),
                      (255, 255, 255), (255, 100, 200)]
            idx = key - Qt.Key_1
            if 0 <= idx < len(colors):
                rgb = colors[idx]
                self.window.set_color(QColor(*rgb, 255))

    def show_help(self):
        """Показать справку"""
        print("""
        Горячие клавиши:
        F2 - Режим рисования
        F4 - Затухание линий
        ESC - Выход из режима / сворачивание

        Режимы рисования:
        F - Свободное рисование
        L - Прямая линия
        R - Прямоугольник
        C - Круг
        T - Треугольник

        Цвета: 1-8
        Delete - Очистить все
        Ctrl+Z - Отменить
        """)
