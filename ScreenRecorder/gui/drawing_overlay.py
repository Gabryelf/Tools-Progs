"""
Прозрачное окно для рисования поверх экрана
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QColorDialog)
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import (QPainter, QPen, QPixmap, QColor,
                         QPainterPath, QBrush, QCursor)


class DrawingOverlay(QWidget):
    """Прозрачное окно для рисования поверх экрана"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Настройки окна
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        # Получаем размеры экрана
        screen = self.screen().size()
        self.setGeometry(0, 0, screen.width(), screen.height())

        # Настройки рисования
        self.drawing = False
        self.last_point = None
        self.current_path = None
        self.paths = []  # Список нарисованных путей

        # Настройки кисти
        self.pen_color = QColor(255, 50, 50, 200)  # Красный с прозрачностью
        self.pen_width = 4
        self.eraser_mode = False
        self.temp_paths = []  # Для отмены

        # Создаем изображение
        self.image = QPixmap(self.size())
        self.image.fill(Qt.transparent)

        self.setMouseTracking(True)

    def paintEvent(self, event):
        """Отрисовка"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рисуем сохраненное изображение
        painter.drawPixmap(0, 0, self.image)

        # Рисуем текущий путь
        if self.current_path and not self.current_path.isEmpty():
            painter.setPen(QPen(self.pen_color, self.pen_width,
                                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(self.current_path)

    def mousePressEvent(self, event):
        """Начало рисования"""
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

            # Создаем новый путь
            self.current_path = QPainterPath()
            self.current_path.moveTo(self.last_point)

    def mouseMoveEvent(self, event):
        """Рисование"""
        if self.drawing and self.current_path:
            current_point = event.pos()

            # Проверяем, что точка в пределах окна
            if self.rect().contains(current_point):
                self.current_path.lineTo(current_point)
                self.update()

    def mouseReleaseEvent(self, event):
        """Завершение рисования"""
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False

            if self.current_path and not self.current_path.isEmpty():
                # Сохраняем путь в изображение
                painter = QPainter(self.image)
                painter.setPen(QPen(self.pen_color, self.pen_width,
                                    Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawPath(self.current_path)
                painter.end()

                # Сохраняем путь для возможности отмены
                self.paths.append(self.current_path)
                self.current_path = None
                self.update()

    def clear_drawing(self):
        """Очистить все рисунки"""
        self.image.fill(Qt.transparent)
        self.paths.clear()
        self.current_path = None
        self.update()

    def undo_last(self):
        """Отменить последнее действие"""
        if self.paths:
            self.paths.pop()
            # Перерисовываем все пути
            self.image.fill(Qt.transparent)
            painter = QPainter(self.image)
            for path in self.paths:
                painter.setPen(QPen(self.pen_color, self.pen_width,
                                    Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawPath(path)
            painter.end()
            self.update()

    def set_color(self, color):
        """Установить цвет"""
        self.pen_color = color

    def set_width(self, width):
        """Установить толщину"""
        self.pen_width = width

    def toggle_eraser(self, enabled):
        """Включить/выключить ластик"""
        self.eraser_mode = enabled
        if enabled:
            self.pen_color = QColor(255, 255, 255, 255)  # Белый = стирание
        else:
            self.pen_color = QColor(255, 50, 50, 200)  # Возвращаем красный

    def get_image(self):
        """Получить изображение с рисунками"""
        return self.image
