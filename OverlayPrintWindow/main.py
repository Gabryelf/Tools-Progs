# ================================================================================
# Main Application - active point - точка входа в главное приложение
# ================================================================================

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor

from src.core.overlay_window import OverlayWindow


class Main:

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш клавиатуры"""
        if event.key() == Qt.Key_Escape:
            # Закрыть программу
            self.close()
        elif event.key() == Qt.Key_C:
            # Очистить все линии
            self.lines.clear()
            self.update()
            print("Все линии очищены")
        elif event.key() == Qt.Key_R:
            # Красный цвет
            self.pen_color = QColor(255, 0, 0, 200)
            print("Цвет изменен на красный")
        elif event.key() == Qt.Key_G:
            # Зеленый цвет
            self.pen_color = QColor(0, 255, 0, 200)
            print("Цвет изменен на зеленый")
        elif event.key() == Qt.Key_B:
            # Синий цвет
            self.pen_color = QColor(0, 0, 255, 200)
            print("Цвет изменен на синий")
        elif event.key() == Qt.Key_Y:
            # Желтый цвет
            self.pen_color = QColor(255, 255, 0, 200)
            print("Цвет изменен на желтый")
        elif event.key() == Qt.Key_1:
            # Толщина 3
            self.pen_width = 3
            print(f"Толщина линии: {self.pen_width}")
        elif event.key() == Qt.Key_2:
            # Толщина 5
            self.pen_width = 5
            print(f"Толщина линии: {self.pen_width}")
        elif event.key() == Qt.Key_3:
            # Толщина 10
            self.pen_width = 10
            print(f"Толщина линии: {self.pen_width}")
        elif event.key() == Qt.Key_4:
            # Толщина 20
            self.pen_width = 20
            print(f"Толщина линии: {self.pen_width}")


def main():
    # Создаем приложение Qt
    app = QApplication(sys.argv)

    # Создаем и показываем окно
    window = OverlayWindow()

    # Выводим подсказки в консоль
    print("\n" + "=" * 50)
    print("УПРАВЛЕНИЕ ПРОГРАММОЙ:")
    print("=" * 50)
    print("ESC - Закрыть программу")
    print("C   - Очистить все линии")
    print("R   - Красный цвет")
    print("G   - Зеленый цвет")
    print("B   - Синий цвет")
    print("Y   - Желтый цвет")
    print("1-4 - Толщина линии (3, 5, 10, 20)")
    print("=" * 50)
    print("Нажмите и удерживайте ЛКМ для рисования\n")

    # Запускаем цикл обработки событий
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
