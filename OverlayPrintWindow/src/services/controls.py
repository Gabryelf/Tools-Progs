from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class Controller:
    def __init__(self, window):
        """
        Конструктор контроллера

        Args:
            window: Ссылка на окно (OverlayWindow)
        """
        self.window = window

    def handle_key_press(self, event):
        """
        Обработка нажатий клавиш клавиатуры

        Args:
            event: Событие клавиатуры
        """
        if event.key() == Qt.Key_Escape:
            # Закрыть программу
            self.window.close()

        elif event.key() == Qt.Key_C:
            # Очистить все линии
            self.window.lines.clear()
            self.window.update()
            print("Все линии очищены")

        elif event.key() == Qt.Key_R:
            # Красный цвет
            self.window.pen_color = QColor(255, 0, 0, 200)
            print("Цвет изменен на красный")

        elif event.key() == Qt.Key_G:
            # Зеленый цвет
            self.window.pen_color = QColor(0, 255, 0, 200)
            print("Цвет изменен на зеленый")

        elif event.key() == Qt.Key_B:
            # Синий цвет
            self.window.pen_color = QColor(0, 0, 255, 200)
            print("Цвет изменен на синий")

        elif event.key() == Qt.Key_Y:
            # Желтый цвет
            self.window.pen_color = QColor(255, 255, 0, 200)
            print("Цвет изменен на желтый")

        elif event.key() == Qt.Key_1:
            # Толщина 3
            self.window.pen_width = 3
            print(f"Толщина линии: {self.window.pen_width}")

        elif event.key() == Qt.Key_2:
            # Толщина 5
            self.window.pen_width = 5
            print(f"Толщина линии: {self.window.pen_width}")

        elif event.key() == Qt.Key_3:
            # Толщина 10
            self.window.pen_width = 10
            print(f"Толщина линии: {self.window.pen_width}")

        elif event.key() == Qt.Key_4:
            # Толщина 20
            self.window.pen_width = 20
            print(f"Толщина линии: {self.window.pen_width}")
