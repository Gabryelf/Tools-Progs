"""Движок рисования - управление линиями и состояниями"""
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QColor
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
from src.utils.constants import DEFAULT_PEN

class DrawingMode(Enum):
    FREE = "free"
    LINE = "line"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    TRIANGLE = "triangle"

class DrawingEngine:
    """Управляет данными рисования"""

    def __init__(self):
        self.lines: List[List[QPoint]] = []
        self.current_line: List[QPoint] = []
        self.current_shape_start: Optional[QPoint] = None
        self.current_shape_end: Optional[QPoint] = None
        self.history: List[List[List[QPoint]]] = []
        self.shape_history: List[List[Dict[str, Any]]] = []
        self.shapes: List[Dict[str, Any]] = []

        self.color = QColor(*DEFAULT_PEN['color'], DEFAULT_PEN['alpha'])
        self.width = DEFAULT_PEN['width']
        self.is_drawing = False
        self.is_active = False
        self.has_changes = False
        self.drawing_mode = DrawingMode.FREE

        # Для временных линий (затухание)
        self.temp_lines: List[Dict[str, Any]] = []

    def start_drawing(self, pos: QPoint):
        """Начать рисование"""
        self.is_drawing = True

        if self.drawing_mode == DrawingMode.FREE:
            self.current_line = [pos]
        else:
            self.current_shape_start = pos
            self.current_shape_end = pos

    def add_point(self, pos: QPoint):
        """Добавить точку в текущую линию"""
        if not self.is_drawing:
            return

        if self.drawing_mode == DrawingMode.FREE:
            self.current_line.append(pos)
            self.has_changes = True
        else:
            self.current_shape_end = pos
            self.has_changes = True

    def stop_drawing(self):
        """Завершить рисование"""
        if not self.is_drawing:
            return

        self.is_drawing = False

        if self.drawing_mode == DrawingMode.FREE:
            if len(self.current_line) > 1:
                self.history.append([line.copy() for line in self.lines])
                self.lines.append(self.current_line.copy())
                self.has_changes = True
            self.current_line = []
        else:
            if self.current_shape_start and self.current_shape_end:
                # Проверяем, что есть расстояние между точками
                if (self.current_shape_start.x() != self.current_shape_end.x() or
                    self.current_shape_start.y() != self.current_shape_end.y()):

                    shape = self._create_shape_data()
                    if shape:
                        self.shape_history.append([s.copy() for s in self.shapes])
                        self.shapes.append(shape)
                        self.has_changes = True

            self.current_shape_start = None
            self.current_shape_end = None

    def _create_shape_data(self) -> Optional[Dict[str, Any]]:
        """Создает данные фигуры"""
        start = self.current_shape_start
        end = self.current_shape_end

        if not start or not end:
            return None

        if self.drawing_mode == DrawingMode.LINE:
            return {
                'type': 'line',
                'start': QPoint(start.x(), start.y()),
                'end': QPoint(end.x(), end.y()),
                'color': QColor(self.color),
                'width': self.width
            }
        elif self.drawing_mode == DrawingMode.RECTANGLE:
            rect = QRect(start, end).normalized()
            if rect.width() > 2 and rect.height() > 2:
                return {
                    'type': 'rectangle',
                    'rect': rect,
                    'color': QColor(self.color),
                    'width': self.width
                }
        elif self.drawing_mode == DrawingMode.CIRCLE:
            center = QPoint((start.x() + end.x()) // 2, (start.y() + end.y()) // 2)
            radius = max(abs(end.x() - start.x()) // 2, abs(end.y() - start.y()) // 2)
            if radius > 2:
                return {
                    'type': 'circle',
                    'center': center,
                    'radius': radius,
                    'color': QColor(self.color),
                    'width': self.width
                }
        elif self.drawing_mode == DrawingMode.TRIANGLE:
            # Создаем треугольник
            points = [
                QPoint(start.x(), end.y()),  # Левая нижняя
                QPoint(end.x(), end.y()),     # Правая нижняя
                QPoint((start.x() + end.x()) // 2, start.y())  # Верхняя
            ]
            # Проверяем, что точки не совпадают
            if (points[0].x() != points[1].x() or points[0].y() != points[1].y()):
                return {
                    'type': 'triangle',
                    'points': points,
                    'color': QColor(self.color),
                    'width': self.width
                }
        return None

    def clear_all(self):
        """Очистить все линии"""
        if self.lines or self.shapes:
            self.history.append([line.copy() for line in self.lines])
            self.shape_history.append([s.copy() for s in self.shapes])
            self.lines.clear()
            self.shapes.clear()
            self.current_line.clear()
            self.current_shape_start = None
            self.current_shape_end = None
            self.has_changes = True

    def undo(self) -> bool:
        """Отменить последнее действие"""
        if self.shapes and self.shape_history:
            self.shapes = self.shape_history.pop()
            self.has_changes = True
            return True
        elif self.lines and self.history:
            self.lines = self.history.pop()
            self.has_changes = True
            return True
        return False

    def set_color(self, color: QColor):
        """Установить цвет"""
        self.color = QColor(color)

    def set_width(self, width: int):
        """Установить толщину"""
        self.width = max(1, min(30, width))

    def set_mode(self, mode: DrawingMode):
        """Установить режим рисования"""
        self.drawing_mode = mode
        self.is_drawing = False
        self.current_line = []
        self.current_shape_start = None
        self.current_shape_end = None

    def set_active(self, active: bool):
        """Установить режим рисования"""
        self.is_active = active
        if not active:
            self.is_drawing = False
            self.current_line = []
            self.current_shape_start = None
            self.current_shape_end = None

    def get_line_count(self) -> int:
        """Получить количество линий"""
        return len(self.lines) + len(self.shapes)

    def has_undo(self) -> bool:
        """Есть ли что отменять"""
        return len(self.lines) > 0 or len(self.shapes) > 0

    def add_temp_line(self, line_data: dict):
        """Добавить временную линию"""
        self.temp_lines.append(line_data)
        self.has_changes = True

    def clear_temp_lines(self):
        """Очистить временные линии"""
        if self.temp_lines:
            self.temp_lines.clear()
            self.has_changes = True
