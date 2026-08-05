"""Сервис управления таймерами для затухания линий"""
from PyQt5.QtCore import QTimer, QPoint, QMutex, QMutexLocker, QRect
from PyQt5.QtGui import QColor
from typing import List, Dict, Any
import time
from math import cos, sin

class TimerService:
    """Управляет временными линиями с затуханием"""
    def __init__(self, overlay_window):
        self.overlay = overlay_window
        self.temp_items = []
        self.mutex = QMutex()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_fading)
        self.timer.start(100)  # 10 fps
        self.is_running = True

    def _copy_line(self, line: List[QPoint]) -> List[QPoint]:
        """Создает копию линии"""
        return [QPoint(p.x(), p.y()) for p in line]

    def _copy_shape(self, shape: Dict[str, Any]) -> Dict[str, Any]:
        """Создает копию фигуры"""
        try:
            shape_copy = shape.copy()
            shape_type = shape_copy.get('type')

            if shape_type == 'line':
                shape_copy['start'] = QPoint(shape['start'].x(), shape['start'].y())
                shape_copy['end'] = QPoint(shape['end'].x(), shape['end'].y())
            elif shape_type == 'rectangle':
                rect = shape.get('rect')
                if rect:
                    shape_copy['rect'] = QRect(rect.x(), rect.y(), rect.width(), rect.height())
            elif shape_type == 'circle':
                shape_copy['center'] = QPoint(shape['center'].x(), shape['center'].y())
                shape_copy['radius'] = shape['radius']
            elif shape_type == 'triangle':
                shape_copy['points'] = [QPoint(p.x(), p.y()) for p in shape['points']]

            # Копируем цвет
            if 'color' in shape_copy:
                color = shape['color']
                if isinstance(color, QColor):
                    shape_copy['color'] = QColor(color)
                elif isinstance(color, (tuple, list)):
                    shape_copy['color'] = QColor(*color[:3], 255 if len(color) < 4 else color[3])

            return shape_copy
        except Exception as e:
            print(f"Ошибка в _copy_shape: {e}")
            return shape.copy()

    def add_line(self, line: List[QPoint], duration: float = 3.0):
        """Добавить линию с затуханием"""
        try:
            if not line or len(line) < 2:
                return
            with QMutexLocker(self.mutex):
                # Создаем копию линии
                line_copy = self._copy_line(line)
                color = QColor(self.overlay.engine.color)
                temp_item = {
                    'type': 'line',
                    'lines': [line_copy],
                    'start_time': time.time(),
                    'duration': duration,
                    'opacity': 1.0,
                    'color': color,
                    'width': self.overlay.engine.width
                }
                self.temp_items.append(temp_item)
                self._update_overlay()
        except Exception as e:
            print(f"Ошибка в add_line: {e}")

    def add_shape(self, shape: Dict[str, Any], duration: float = 3.0):
        """Добавить фигуру с затуханием"""
        try:
            if not shape:
                return
            with QMutexLocker(self.mutex):
                # Создаем копию фигуры
                shape_copy = self._copy_shape(shape)
                temp_item = {
                    'type': 'shape',
                    'shape': shape_copy,
                    'start_time': time.time(),
                    'duration': duration,
                    'opacity': 1.0
                }
                self.temp_items.append(temp_item)
                self._update_overlay()
        except Exception as e:
            print(f"Ошибка в add_shape: {e}")

    def update_fading(self):
        """Обновляет прозрачность линий"""
        try:
            if not self.temp_items:
                return
            with QMutexLocker(self.mutex):
                current_time = time.time()
                items_to_remove = []
                for i, temp_item in enumerate(self.temp_items):
                    elapsed = current_time - temp_item['start_time']
                    if elapsed >= temp_item['duration']:
                        items_to_remove.append(i)
                    else:
                        # Рассчитываем прозрачность (сначала ждем, потом затухаем)
                        half_duration = temp_item['duration'] / 2
                        if elapsed < half_duration:
                            temp_item['opacity'] = 1.0
                        else:
                            fade_time = elapsed - half_duration
                            fade_duration = half_duration
                            temp_item['opacity'] = max(0, 1.0 - (fade_time / fade_duration))
                # Удаляем истекшие элементы (в обратном порядке)
                for i in sorted(items_to_remove, reverse=True):
                    del self.temp_items[i]
                # Обновляем оверлей
                if items_to_remove or self.temp_items:
                    self._update_overlay()
        except Exception as e:
            print(f"Ошибка в update_fading: {e}")

    def _update_overlay(self):
        """Обновляет оверлей с временными элементами"""
        try:
            # Преобразуем временные элементы в формат для отрисовки
            temp_lines = []
            for item in self.temp_items:
                if item['type'] == 'line':
                    color = item.get('color')
                    if isinstance(color, QColor):
                        color_data = color
                    else:
                        color_data = QColor(255, 0, 0, 255)

                    temp_lines.append({
                        'lines': item['lines'],
                        'opacity': item['opacity'],
                        'color': color_data,
                        'width': item.get('width', 3)
                    })
                elif item['type'] == 'shape':
                    # Добавляем фигуру как временную для затухания
                    shape = item['shape']
                    if shape:
                        # Преобразуем фигуру в линии для затухания
                        shape_lines = self._shape_to_lines(shape)
                        if shape_lines:
                            color = shape.get('color')
                            if isinstance(color, QColor):
                                color_data = color
                            else:
                                color_data = QColor(255, 0, 0, 255)

                            temp_lines.append({
                                'lines': shape_lines,
                                'opacity': item['opacity'],
                                'color': color_data,
                                'width': shape.get('width', 3)
                            })
            self.overlay.engine.temp_lines = temp_lines
            self.overlay.update()
        except Exception as e:
            print(f"Ошибка в _update_overlay: {e}")

    def _shape_to_lines(self, shape: Dict[str, Any]) -> List[List[QPoint]]:
        """Преобразует фигуру в линии для затухания"""
        try:
            shape_type = shape.get('type')
            if not shape_type:
                return []

            if shape_type == 'line':
                start = shape.get('start')
                end = shape.get('end')
                if start and end:
                    return [[QPoint(start.x(), start.y()), QPoint(end.x(), end.y())]]

            elif shape_type == 'rectangle':
                rect = shape.get('rect')
                if rect:
                    points = [
                        QPoint(rect.x(), rect.y()),
                        QPoint(rect.x() + rect.width(), rect.y()),
                        QPoint(rect.x() + rect.width(), rect.y() + rect.height()),
                        QPoint(rect.x(), rect.y() + rect.height())
                    ]
                    return [
                        [points[0], points[1]],
                        [points[1], points[2]],
                        [points[2], points[3]],
                        [points[3], points[0]]
                    ]

            elif shape_type == 'circle':
                # Для круга преобразуем в многоугольник
                center = shape.get('center')
                radius = shape.get('radius', 10)
                if center and radius > 0:
                    lines = []
                    steps = 36  # Количество сегментов
                    for i in range(steps):
                        angle1 = 2 * 3.14159 * i / steps
                        angle2 = 2 * 3.14159 * (i + 1) / steps
                        p1 = QPoint(
                            int(center.x() + radius * cos(angle1)),
                            int(center.y() + radius * sin(angle1))
                        )
                        p2 = QPoint(
                            int(center.x() + radius * cos(angle2)),
                            int(center.y() + radius * sin(angle2))
                        )
                        lines.append([p1, p2])
                    return lines

            elif shape_type == 'triangle':
                points = shape.get('points')
                if points and len(points) == 3:
                    return [
                        [QPoint(points[0].x(), points[0].y()), QPoint(points[1].x(), points[1].y())],
                        [QPoint(points[1].x(), points[1].y()), QPoint(points[2].x(), points[2].y())],
                        [QPoint(points[2].x(), points[2].y()), QPoint(points[0].x(), points[0].y())]
                    ]

            return []
        except Exception as e:
            print(f"Ошибка в _shape_to_lines: {e}")
            return []

    def clear_all(self):
        """Очищает все временные линии"""
        try:
            with QMutexLocker(self.mutex):
                self.temp_items.clear()
                self.overlay.engine.temp_lines.clear()
                self.overlay.update()
        except Exception as e:
            print(f"Ошибка в clear_all: {e}")

    def stop(self):
        """Останавливает сервис"""
        self.is_running = False
        self.timer.stop()
