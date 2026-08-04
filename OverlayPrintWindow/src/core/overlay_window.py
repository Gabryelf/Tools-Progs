# ================================================================================
# Overlay Window - main window - главный слой приложения
# ================================================================================
from PyQt5.QtWidgets import QWidget, QDesktopWidget
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QMouseEvent


class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Настройка флагов окна
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        # Настройка прозрачности
        self.setAttribute(Qt.WA_TranslucentBackground)
        # НЕ используем WA_TransparentForMouseEvents

        # Установка размера на весь экран
        screen_geometry = QDesktopWidget().screenGeometry()
        self.setGeometry(screen_geometry)

        # Переменные для рисования
        self.drawing = False
        self.lines = []
        self.current_line = []

        # Настройки пера
        self.pen_color = QColor(255, 0, 0, 200)
        self.pen_width = 8

        self.setCursor(Qt.CrossCursor)
        self.showFullScreen()

        # Включаем захват мыши для получения событий вне окна
        self.grabMouse()

        print("Оверлей готов к рисованию")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.transparent)
        painter.drawRect(self.rect())

        pen = QPen(
            self.pen_color,
            self.pen_width,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.RoundJoin
        )
        painter.setPen(pen)

        for line in self.lines:
            if len(line) > 1:
                for i in range(len(line) - 1):
                    painter.drawLine(line[i], line[i + 1])

        if len(self.current_line) > 1:
            for i in range(len(self.current_line) - 1):
                painter.drawLine(self.current_line[i], self.current_line[i + 1])

    def mousePressEvent(self, event):
        print(f"MousePressEvent: pos=({event.pos().x()}, {event.pos().y()})")
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.current_line = [event.pos()]
            print(f"Начало рисования в точке: {event.pos().x()}, {event.pos().y()}")

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.current_line.append(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if len(self.current_line) > 1:
                self.lines.append(self.current_line)
                print(f"Линия сохранена. Всего линий: {len(self.lines)}")
            self.current_line = []
            self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_C:
            self.lines.clear()
            self.update()
            print("Все линии очищены")
        elif hasattr(self, 'controller'):
            self.controller.handle_key_press(event)

    def set_controller(self, controller):
        self.controller = controller

