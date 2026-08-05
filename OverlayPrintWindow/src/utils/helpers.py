"""Вспомогательные функции"""


def clamp(value, min_val, max_val):
    """Ограничивает значение в заданных пределах"""
    return max(min_val, min(value, max_val))


def distance(point1, point2):
    """Вычисляет расстояние между двумя точками"""
    from math import sqrt
    return sqrt((point1.x() - point2.x()) ** 2 + (point1.y() - point2.y()) ** 2)


def rect_from_points(p1, p2):
    """Создает прямоугольник из двух точек"""
    from PyQt5.QtCore import QRect
    return QRect(p1, p2).normalized()
