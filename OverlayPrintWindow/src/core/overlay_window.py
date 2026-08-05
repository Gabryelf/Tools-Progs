"""Окно-оверлей для рисования поверх экрана"""
from PyQt5.QtWidgets import QWidget, QDesktopWidget
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from pynput import mouse
import threading
from src.core.drawing_engine import DrawingEngine, DrawingMode
from src.services.timer_service import TimerService

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

        # Сервис таймера
        self.timer_service = TimerService(self)
        self.fading_enabled = False

        # Таймер для обновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(50)  # 20 fps

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

                # Проверяем, что позиция в пределах экрана
                if 0 <= pos.x() <= self.width() and 0 <= pos.y() <= self.height():
                    if pressed:
                        self.engine.start_drawing(pos)
                    else:
                        self.engine.stop_drawing()
                        # Если включено затухание, добавляем в таймер
                        if self.fading_enabled:
                            # Сохраняем последнюю нарисованную линию
                            if self.engine.lines:
                                last_line = self.engine.lines[-1]
                                if last_line and len(last_line) > 1:
                                    self.timer_service.add_line(last_line, 3.0)
                            # Или последнюю фигуру
                            elif self.engine.shapes:
                                last_shape = self.engine.shapes[-1]
                                if last_shape:
                                    self.timer_service.add_shape(last_shape, 3.0)

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

        # Рисуем все линии
        self._draw_lines(painter)

        # Рисуем фигуры
        self._draw_shapes(painter)

        # Рисуем текущую фигуру или линию
        self._draw_current(painter)

        # Рисуем временные линии (затухание)
        self._draw_temp_lines(painter)

    def _draw_lines(self, painter):
        """Рисует все линии"""
        for line in self.engine.lines:
            if len(line) > 1:
                pen = QPen(self.engine.color, self.engine.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)
                for i in range(len(line) - 1):
                    painter.drawLine(line[i], line[i + 1])

    def _draw_temp_lines(self, painter):
        """Рисует временные линии с затуханием"""
        for temp_data in self.engine.temp_lines:
            if 'lines' in temp_data:
                alpha = int(255 * temp_data.get('opacity', 1.0))
                color = QColor(temp_data.get('color', [255, 0, 0, 255]))
                color.setAlpha(alpha)

                pen = QPen(color, temp_data.get('width', 3), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)

                for line in temp_data['lines']:
                    if len(line) > 1:
                        for i in range(len(line) - 1):
                            painter.drawLine(line[i], line[i + 1])

    def _draw_shapes(self, painter):
        """Рисует фигуры"""
        for shape in self.engine.shapes:
            shape_type = shape.get('type')
            if shape_type == 'rectangle':
                self._draw_rectangle(painter, shape)
            elif shape_type == 'circle':
                self._draw_circle(painter, shape)
            elif shape_type == 'triangle':
                self._draw_triangle(painter, shape)
            elif shape_type == 'line':
                self._draw_straight_line(painter, shape)

    def _draw_rectangle(self, painter, shape):
        """Рисует прямоугольник"""
        pen = QPen(shape['color'], shape['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawRect(shape['rect'])

    def _draw_circle(self, painter, shape):
        """Рисует круг"""
        pen = QPen(shape['color'], shape['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawEllipse(shape['center'], shape['radius'], shape['radius'])

    def _draw_triangle(self, painter, shape):
        """Рисует треугольник"""
        pen = QPen(shape['color'], shape['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        points = shape['points']
        if len(points) == 3:
            painter.drawLine(points[0], points[1])
            painter.drawLine(points[1], points[2])
            painter.drawLine(points[2], points[0])

    def _draw_straight_line(self, painter, shape):
        """Рисует прямую линию"""
        pen = QPen(shape['color'], shape['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(shape['start'], shape['end'])

    def _draw_current(self, painter):
        """Рисует текущую линию или фигуру"""
        if self.engine.drawing_mode == DrawingMode.FREE:
            # Текущая линия
            if len(self.engine.current_line) > 1:
                pen = QPen(self.engine.color, self.engine.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)
                for i in range(len(self.engine.current_line) - 1):
                    painter.drawLine(
                        self.engine.current_line[i],
                        self.engine.current_line[i + 1]
                    )
        else:
            # Текущая фигура
            if self.engine.current_shape_start and self.engine.current_shape_end:
                start = self.engine.current_shape_start
                end = self.engine.current_shape_end

                pen = QPen(self.engine.color, self.engine.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)

                if self.engine.drawing_mode == DrawingMode.LINE:
                    painter.drawLine(start, end)
                elif self.engine.drawing_mode == DrawingMode.RECTANGLE:
                    rect = QRect(start, end).normalized()
                    painter.drawRect(rect)
                elif self.engine.drawing_mode == DrawingMode.CIRCLE:
                    center = QPoint((start.x() + end.x()) // 2, (start.y() + end.y()) // 2)
                    radius = max(abs(end.x() - start.x()) // 2, abs(end.y() - start.y()) // 2)
                    if radius > 1:
                        painter.drawEllipse(center, radius, radius)
                elif self.engine.drawing_mode == DrawingMode.TRIANGLE:
                    points = [
                        QPoint(start.x(), end.y()),
                        QPoint(end.x(), end.y()),
                        QPoint((start.x() + end.x()) // 2, start.y())
                    ]
                    painter.drawLine(points[0], points[1])
                    painter.drawLine(points[1], points[2])
                    painter.drawLine(points[2], points[0])

    def set_drawing_mode(self, enabled: bool):
        """Вкл/Выкл режим рисования"""
        self.engine.set_active(enabled)

        if enabled:
            self.start_mouse_listener()
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.setCursor(Qt.CrossCursor)
            print("🟢 Режим рисования ВКЛЮЧЕН")
        else:
            self.stop_mouse_listener()
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.setCursor(Qt.ArrowCursor)
            self.engine.is_drawing = False
            self.engine.current_line = []
            self.engine.current_shape_start = None
            self.engine.current_shape_end = None
            print("🔴 Режим рисования ВЫКЛЮЧЕН")

        self.update()

    def set_drawing_mode_type(self, mode: DrawingMode):
        """Установить тип рисования"""
        self.engine.set_mode(mode)
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

    def toggle_fading(self):
        """Включить/выключить режим затухания"""
        self.fading_enabled = not self.fading_enabled
        if not self.fading_enabled:
            self.timer_service.clear_all()
            self.engine.clear_temp_lines()
        return self.fading_enabled

    def closeEvent(self, event):
        self.stop_mouse_listener()
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.update_timer.stop()
        super().closeEvent(event)
