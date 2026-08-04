"""Окно-оверлей для рисования поверх экрана"""

from PyQt5.QtWidgets import QWidget, QDesktopWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor
from pynput import mouse
import threading
from src.core.drawing_engine import DrawingEngine


class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Настройка окна
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # Полный экран
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(screen)

        # Движок рисования
        self.engine = DrawingEngine()

        # Слушатель мыши
        self.mouse_listener = None
        self.listener_running = False

        self.showFullScreen()

    def start_mouse_listener(self):
        """Запускает глобальный слушатель мыши"""
        if self.listener_running:
            return

        def on_click(x, y, button, pressed):
            if not self.engine.is_active:
                return

            if button == mouse.Button.left:
                pos = self.mapFromGlobal(QPoint(x, y))
                if pressed:
                    self.engine.start_drawing(pos)
                else:
                    self.engine.stop_drawing()
                    self.update()

        def on_move(x, y):
            if not self.engine.is_active or not self.engine.is_drawing:
                return

            pos = self.mapFromGlobal(QPoint(x, y))
            # Проверяем, что позиция в пределах экрана
            if 0 <= pos.x() <= self.width() and 0 <= pos.y() <= self.height():
                self.engine.add_point(pos)
                self.update()

        # Запускаем в отдельном потоке
        self.mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()
        self.listener_running = True

    def stop_mouse_listener(self):
        """Останавливает слушатель мыши"""
        if self.mouse_listener and self.listener_running:
            self.mouse_listener.stop()
            self.listener_running = False
            self.mouse_listener = None

    def paintEvent(self, event):
        """Отрисовка"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Прозрачный фон
        painter.setBrush(Qt.transparent)
        painter.drawRect(self.rect())

        # Настройка пера
        pen = QPen(
            self.engine.color,
            self.engine.width,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.RoundJoin
        )
        painter.setPen(pen)

        # Рисуем все линии
        for line in self.engine.lines:
            if len(line) > 1:
                for i in range(len(line) - 1):
                    painter.drawLine(line[i], line[i + 1])

        # Текущая линия
        if len(self.engine.current_line) > 1:
            for i in range(len(self.engine.current_line) - 1):
                painter.drawLine(
                    self.engine.current_line[i],
                    self.engine.current_line[i + 1]
                )

    def set_drawing_mode(self, enabled: bool):
        """Вкл/Выкл режим рисования"""
        self.engine.set_active(enabled)

        if enabled:
            # Запускаем глобальный слушатель
            self.start_mouse_listener()
            # Делаем окно непрозрачным для событий мыши
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.setCursor(Qt.CrossCursor)
            print("🟢 Режим рисования ВКЛЮЧЕН")
        else:
            # Останавливаем слушатель
            self.stop_mouse_listener()
            # Делаем окно прозрачным для событий мыши
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.setCursor(Qt.ArrowCursor)
            self.engine.is_drawing = False
            self.engine.current_line = []
            print("🔴 Режим рисования ВЫКЛЮЧЕН")

        self.update()

    def clear_all(self):
        self.engine.clear_all()
        self.update()

    def undo(self):
        if self.engine.undo():
            self.update()
            return True
        return False

    def set_color(self, color):
        self.engine.set_color(color)

    def set_width(self, width):
        self.engine.set_width(width)

    def closeEvent(self, event):
        self.stop_mouse_listener()
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        super().closeEvent(event)
