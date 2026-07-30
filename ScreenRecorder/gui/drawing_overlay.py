"""
Прозрачное окно для рисования поверх экрана
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QMutex, QMutexLocker
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor, QPainterPath, QCursor
import numpy as np


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
        self.paths = []
        self.has_drawing = False  # Флаг наличия рисунков

        # Настройки кисти - яркий красный
        self.pen_color = QColor(255, 0, 0, 255)
        self.pen_width = 5

        # Изображение для рисования
        self.image = QPixmap(self.size())
        self.image.fill(Qt.transparent)

        # Мьютекс
        self.mutex = QMutex()

        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)

        print("✅ DrawingOverlay создан")
        print(f"📐 Размер оверлея: {self.width()}x{self.height()}")

    def paintEvent(self, event):
        """Отрисовка"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рисуем сохраненное изображение
        painter.drawPixmap(0, 0, self.image)

        # Рисуем текущий путь (то, что рисуется прямо сейчас)
        if self.current_path and not self.current_path.isEmpty():
            painter.setPen(QPen(self.pen_color, self.pen_width,
                                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(self.current_path)

    def mousePressEvent(self, event):
        """Начало рисования"""
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
            self.current_path = QPainterPath()
            self.current_path.moveTo(self.last_point)
            print(f"🖍️ Начало рисования в точке: ({event.pos().x()}, {event.pos().y()})")

    def mouseMoveEvent(self, event):
        """Рисование"""
        if self.drawing and self.current_path:
            current_point = event.pos()
            if self.rect().contains(current_point):
                self.current_path.lineTo(current_point)
                # Принудительно перерисовываем
                self.update()

    def mouseReleaseEvent(self, event):
        """Завершение рисования"""
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.current_path and not self.current_path.isEmpty():
                with QMutexLocker(self.mutex):
                    # Сохраняем путь в изображение
                    painter = QPainter(self.image)
                    painter.setPen(QPen(self.pen_color, self.pen_width,
                                        Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    painter.drawPath(self.current_path)
                    painter.end()

                    # Сохраняем путь для отмены
                    self.paths.append(self.current_path)
                    self.has_drawing = True
                    self.current_path = None

                    print(f"✅ Рисование завершено, всего путей: {len(self.paths)}")
                    self.update()

    def clear_drawing(self):
        """Очистить все рисунки"""
        with QMutexLocker(self.mutex):
            self.image.fill(Qt.transparent)
            self.paths.clear()
            self.current_path = None
            self.has_drawing = False
            self.update()
        print("🗑️ Все рисунки очищены")

    def undo_last(self):
        """Отменить последнее действие"""
        if self.paths:
            with QMutexLocker(self.mutex):
                self.paths.pop()
                self.image.fill(Qt.transparent)
                painter = QPainter(self.image)
                for path in self.paths:
                    painter.setPen(QPen(self.pen_color, self.pen_width,
                                        Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    painter.drawPath(path)
                painter.end()
                self.has_drawing = len(self.paths) > 0
                self.update()
            print(f"↩️ Отменено, осталось: {len(self.paths)}")

    def set_color(self, color):
        self.pen_color = color
        print(f"🎨 Цвет изменен на: {color.name()}")

    def set_width(self, width):
        self.pen_width = width
        print(f"📏 Толщина: {width}")

    def toggle_eraser(self, enabled):
        if enabled:
            self.pen_color = QColor(255, 255, 255, 255)
            self.setCursor(Qt.BlankCursor)
            print("🧹 Ластик включен")
        else:
            self.pen_color = QColor(255, 0, 0, 255)
            self.setCursor(Qt.CrossCursor)
            print("🖍️ Ластик выключен")

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        self.setFocus()
        print("🖍️ Оверлей показан и активен")

    def get_numpy_array(self):
        """
        Получить изображение как numpy массив RGBA.
        Возвращает None если рисунков нет.
        """
        with QMutexLocker(self.mutex):
            if not self.has_drawing:
                return None

            try:
                # Конвертируем QPixmap в QImage
                qimage = self.image.toImage()
                qimage = qimage.convertToFormat(QImage.Format_RGBA8888)

                width = qimage.width()
                height = qimage.height()

                if width <= 0 or height <= 0:
                    return None

                # Получаем данные
                ptr = qimage.bits()
                ptr.setsize(qimage.byteCount())

                # Создаем numpy массив
                arr = np.array(ptr).reshape(height, width, 4)

                # Проверяем наличие рисунков
                if np.any(arr[:, :, 3] > 10):
                    return arr.copy()

            except Exception as e:
                print(f"⚠️ Ошибка получения массива: {e}")

            return None
