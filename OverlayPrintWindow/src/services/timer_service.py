"""Сервис управления таймерами для затухания линий"""
from PyQt5.QtCore import QTimer, QPoint, QMutex, QMutexLocker
from typing import List, Dict, Any
import time

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

    def add_line(self, line: List[QPoint], duration: float = 3.0):
        """Добавить линию с затуханием"""
        if not line or len(line) < 2:
            return

        with QMutexLocker(self.mutex):
            # Создаем копию линии
            line_copy = [QPoint(p.x(), p.y()) for p in line]

            temp_item = {
                'type': 'line',
                'lines': [line_copy],
                'start_time': time.time(),
                'duration': duration,
                'opacity': 1.0,
                'color': self.overlay.engine.color.getRgb(),
                'width': self.overlay.engine.width
            }

            self.temp_items.append(temp_item)
            self._update_overlay()

    def add_shape(self, shape: Dict[str, Any], duration: float = 3.0):
        """Добавить фигуру с затуханием"""
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
                'opacity': 1.0,
                'color': self.overlay.engine.color.getRgb(),
                'width': self.overlay.engine.width
            }

            self.temp_items.append(temp_item)
            self._update_overlay()

    def _copy_shape(self, shape: Dict[str, Any]) -> Dict[str, Any]:
        """Создает копию фигуры"""
        shape_copy = shape.copy()

        if shape['type'] == 'line':
            shape_copy['start'] = QPoint(shape['start'].x(), shape['start'].y())
            shape_copy['end'] = QPoint(shape['end'].x(), shape['end'].y())
        elif shape['type'] == 'rectangle':
            rect = shape['rect']
            shape_copy['rect'] = rect
        elif shape['type'] == 'circle':
            shape_copy['center'] = QPoint(shape['center'].x(), shape['center'].y())
            shape_copy['radius'] = shape['radius']
        elif shape['type'] == 'triangle':
            shape_copy['points'] = [QPoint(p.x(), p.y()) for p in shape['points']]

        shape_copy['color'] = QColor(shape['color'])
        return shape_copy

    def update_fading(self):
        """Обновляет прозрачность линий"""
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

    def _update_overlay(self):
        """Обновляет оверлей с временными элементами"""
        # Преобразуем временные элементы в формат для отрисовки
        temp_lines = []

        for item in self.temp_items:
            if item['type'] == 'line':
                temp_lines.append({
                    'lines': item['lines'],
                    'opacity': item['opacity'],
                    'color': item['color'],
                    'width': item['width']
                })
            elif item['type'] == 'shape':
                # Для фигур пока не поддерживаем затухание
                # В будущем можно добавить
                pass

        self.overlay.engine.temp_lines = temp_lines
        self.overlay.update()

    def clear_all(self):
        """Очищает все временные линии"""
        with QMutexLocker(self.mutex):
            self.temp_items.clear()
            self.overlay.engine.temp_lines.clear()
            self.overlay.update()

    def stop(self):
        """Останавливает сервис"""
        self.is_running = False
        self.timer.stop()
