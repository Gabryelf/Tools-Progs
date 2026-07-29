"""
Прозрачное окно для рисования поверх экрана
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor, QPainterPath, QBrush, QCursor


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
        self.temp_path = None  # Для временного хранения

        # Настройки кисти
        self.pen_color = QColor(255, 0, 0, 255)  # Ярко-красный
        self.pen_width = 5

        # Создаем изображение для рисования
        self.image = QPixmap(self.size())
        self.image.fill(Qt.transparent)

        self.setMouseTracking(True)

        # Курсор в виде крестика для точности
        self.setCursor(Qt.CrossCursor)

        # Таймер для обновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(50)

        print("✅ DrawingOverlay создан")

    def paintEvent(self, event):
        """Отрисовка"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рисуем сохраненное изображение
        painter.drawPixmap(0, 0, self.image)

        # Рисуем текущий путь (то что рисуется прямо сейчас)
        if self.current_path and not self.current_path.isEmpty():
            painter.setPen(QPen(self.pen_color, self.pen_width,
                                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(self.current_path)

    def mousePressEvent(self, event):
        """Начало рисования"""
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

            # Создаем новый путь
            self.current_path = QPainterPath()
            self.current_path.moveTo(self.last_point)

            print(f"🖍️ Рисование начато в ({self.last_point.x()}, {self.last_point.y()})")

    def mouseMoveEvent(self, event):
        """Рисование"""
        if self.drawing and self.current_path:
            current_point = event.pos()

            # Проверяем, что точка в пределах окна
            if self.rect().contains(current_point):
                self.current_path.lineTo(current_point)
                # Принудительно обновляем
                self.repaint()

    def mouseReleaseEvent(self, event):
        """Завершение рисования"""
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False

            if self.current_path and not self.current_path.isEmpty():
                # Сохраняем путь в изображение
                painter = QPainter(self.image)
                painter.setPen(QPen(self.pen_color, self.pen_width,
                                    Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawPath(self.current_path)
                painter.end()

                # Сохраняем путь для возможности отмены
                self.paths.append(self.current_path)
                self.current_path = None
                self.repaint()

                print(f"✅ Путь сохранен, всего: {len(self.paths)}")

    def clear_drawing(self):
        """Очистить все рисунки"""
        self.image.fill(Qt.transparent)
        self.paths.clear()
        self.current_path = None
        self.repaint()
        print("🗑️ Все рисунки очищены")

    def undo_last(self):
        """Отменить последнее действие"""
        if self.paths:
            self.paths.pop()
            self.image.fill(Qt.transparent)
            painter = QPainter(self.image)
            for path in self.paths:
                painter.setPen(QPen(self.pen_color, self.pen_width,
                                    Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawPath(path)
            painter.end()
            self.repaint()
            print(f"↩️ Отменено, осталось: {len(self.paths)}")

    def set_color(self, color):
        """Установить цвет"""
        self.pen_color = color
        print(f"🎨 Цвет изменен на: {color.name()}")

    def set_width(self, width):
        """Установить толщину"""
        self.pen_width = width
        print(f"📏 Толщина: {width}")

    def toggle_eraser(self, enabled):
        """Включить/выключить ластик"""
        if enabled:
            self.pen_color = QColor(255, 255, 255, 255)
            self.setCursor(Qt.BlankCursor)
            print("🧹 Ластик включен")
        else:
            self.pen_color = QColor(255, 0, 0, 255)
            self.setCursor(Qt.CrossCursor)
            print("🖍️ Ластик выключен")

    def get_image(self):
        """Получить изображение с рисунками"""
        return self.image

    def showEvent(self, event):
        """При показе окна"""
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        print("🖍️ Оверлей показан и активирован")