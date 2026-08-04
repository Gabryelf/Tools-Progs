"""Движок рисования - управление линиями и состояниями"""

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor
from typing import List, Tuple
from src.utils.constants import DEFAULT_PEN


class DrawingEngine:
    """Управляет данными рисования"""

    def __init__(self):
        self.lines: List[List[QPoint]] = []
        self.current_line: List[QPoint] = []
        self.history: List[List[List[QPoint]]] = []

        self.color = QColor(*DEFAULT_PEN['color'], DEFAULT_PEN['alpha'])
        self.width = DEFAULT_PEN['width']

        self.is_drawing = False
        self.is_active = False
        self.has_changes = False

    def start_drawing(self, pos: QPoint):
        """Начать рисование"""
        self.is_drawing = True
        self.current_line = [pos]

    def add_point(self, pos: QPoint):
        """Добавить точку в текущую линию"""
        if self.is_drawing:
            self.current_line.append(pos)
            self.has_changes = True

    def stop_drawing(self):
        """Завершить рисование"""
        if self.is_drawing:
            self.is_drawing = False
            if len(self.current_line) > 1:
                self.history.append([line.copy() for line in self.lines])
                self.lines.append(self.current_line.copy())
                self.has_changes = True
            self.current_line = []

    def clear_all(self):
        """Очистить все линии"""
        if self.lines:
            self.history.append([line.copy() for line in self.lines])
            self.lines.clear()
            self.current_line.clear()
            self.has_changes = True

    def undo(self) -> bool:
        """Отменить последнее действие"""
        if self.lines:
            self.lines.pop()
            self.has_changes = True
            return True
        return False

    def set_color(self, color: QColor):
        """Установить цвет"""
        self.color = color

    def set_width(self, width: int):
        """Установить толщину"""
        self.width = max(1, min(30, width))

    def set_active(self, active: bool):
        """Установить режим рисования"""
        self.is_active = active
        if not active:
            self.is_drawing = False
            self.current_line = []

    def get_line_count(self) -> int:
        """Получить количество линий"""
        return len(self.lines)

    def has_undo(self) -> bool:
        """Есть ли что отменять"""
        return len(self.lines) > 0
