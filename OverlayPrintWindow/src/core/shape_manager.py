"""Менеджер фигур - создание и управление геометрическими фигурами"""
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QColor
from typing import Dict, Any
from enum import Enum


class ShapeType(Enum):
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    TRIANGLE = "triangle"
    LINE = "line"


class ShapeManager:
    """Создает и управляет геометрическими фигурами"""

    @staticmethod
    def create_shape(shape_type, start: QPoint, end: QPoint, color: QColor, width: int) -> Dict[str, Any]:
        """Создать фигуру"""
        if shape_type == ShapeType.RECTANGLE:
            return ShapeManager._create_rectangle(start, end, color, width)
        elif shape_type == ShapeType.CIRCLE:
            return ShapeManager._create_circle(start, end, color, width)
        elif shape_type == ShapeType.TRIANGLE:
            return ShapeManager._create_triangle(start, end, color, width)
        elif shape_type == ShapeType.LINE:
            return ShapeManager._create_line(start, end, color, width)
        return None

    @staticmethod
    def _create_rectangle(start: QPoint, end: QPoint, color: QColor, width: int) -> Dict[str, Any]:
        """Создать прямоугольник"""
        rect = QRect(start, end).normalized()
        return {
            'type': 'rectangle',
            'rect': rect,
            'color': color,
            'width': width
        }

    @staticmethod
    def _create_circle(start: QPoint, end: QPoint, color: QColor, width: int) -> Dict[str, Any]:
        """Создать круг"""
        center = QPoint((start.x() + end.x()) // 2, (start.y() + end.y()) // 2)
        radius = max(abs(end.x() - start.x()) // 2, abs(end.y() - start.y()) // 2)
        return {
            'type': 'circle',
            'center': center,
            'radius': radius,
            'color': color,
            'width': width
        }

    @staticmethod
    def _create_triangle(start: QPoint, end: QPoint, color: QColor, width: int) -> Dict[str, Any]:
        """Создать треугольник"""
        # Создаем равнобедренный треугольник
        base_mid = QPoint((start.x() + end.x()) // 2, end.y())
        height = abs(end.y() - start.y())
        top = QPoint(base_mid.x(), start.y() - height // 2)

        return {
            'type': 'triangle',
            'points': [start, end, top],
            'color': color,
            'width': width
        }

    @staticmethod
    def _create_line(start: QPoint, end: QPoint, color: QColor, width: int) -> Dict[str, Any]:
        """Создать прямую линию"""
        return {
            'type': 'line',
            'start': start,
            'end': end,
            'color': color,
            'width': width
        }
