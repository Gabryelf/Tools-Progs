import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor


class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Настройка флагов окна
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # Без рамки
            Qt.WindowStaysOnTopHint |  # Всегда поверх всех окон
            Qt.Tool  # Не показывать в панели задач
        )

        # Настройка прозрачности
        self.setAttribute(Qt.WA_TranslucentBackground)  # Прозрачный фон
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Клики проходят сквозь

        # Установка размера на весь экран
        screen_geometry = QDesktopWidget().screenGeometry()
        self.setGeometry(screen_geometry)

        # Переменные для рисования
        self.drawing = False  # Флаг: идет ли рисование
        self.lines = []  # Список всех нарисованных линий
        self.current_line = []  # Текущая рисуемая линия

        # Настройки пера (маркера)
        self.pen_color = QColor(255, 0, 0, 200)  # Красный, полупрозрачный
        self.pen_width = 8  # Толщина линии

        # Изменяем курсор для наглядности
        self.setCursor(Qt.CrossCursor)

        # Разворачиваем на полный экран
        self.showFullScreen()

        # Для проверки: рисуем тестовую линию
        test_line = [QPoint(100, 100), QPoint(200, 200), QPoint(300, 100)]
        self.lines.append(test_line)
        self.update()
        print("Тестовая линия нарисована для проверки")

    def paintEvent(self, event):
        """Метод отрисовки всех линий на экране"""
        # Создаем объект для рисования
        painter = QPainter(self)

        # Включаем сглаживание для плавных линий
        painter.setRenderHint(QPainter.Antialiasing)

        # Делаем фон полностью прозрачным
        painter.setBrush(Qt.transparent)
        painter.drawRect(self.rect())

        # Настраиваем перо (цвет, толщина, стиль)
        pen = QPen(
            self.pen_color,  # Цвет
            self.pen_width,  # Толщина
            Qt.SolidLine,  # Сплошная линия
            Qt.RoundCap,  # Закругленные концы
            Qt.RoundJoin  # Закругленные соединения
        )
        painter.setPen(pen)

        # Рисуем все сохраненные линии
        for line in self.lines:
            if len(line) > 1:  # В линии должно быть минимум 2 точки
                for i in range(len(line) - 1):
                    painter.drawLine(line[i], line[i + 1])

        # Рисуем текущую линию (во время рисования)
        if len(self.current_line) > 1:
            for i in range(len(self.current_line) - 1):
                painter.drawLine(self.current_line[i], self.current_line[i + 1])

    def mousePressEvent(self, event):
        """Обработка нажатия кнопки мыши"""
        if event.button() == Qt.LeftButton:
            # Начинаем рисование
            self.drawing = True
            # Создаем новую линию с текущей позицией мыши
            self.current_line = [event.pos()]
            print(f"Начало рисования в точке: {event.pos().x()}, {event.pos().y()}")

    def mouseMoveEvent(self, event):
        """Обработка движения мыши с зажатой кнопкой"""
        if self.drawing:
            # Добавляем новую точку в текущую линию
            self.current_line.append(event.pos())
            # Перерисовываем окно
            self.update()

    def mouseReleaseEvent(self, event):
        """Обработка отпускания кнопки мыши"""
        if event.button() == Qt.LeftButton and self.drawing:
            # Завершаем рисование
            self.drawing = False

            # Если линия имеет хотя бы 2 точки - сохраняем её
            if len(self.current_line) > 1:
                self.lines.append(self.current_line)
                print(f"Линия сохранена. Всего линий: {len(self.lines)}")

            # Очищаем текущую линию
            self.current_line = []
            # Перерисовываем окно
            self.update()

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш клавиатуры"""
        if event.key() == Qt.Key_Escape:
            # Закрыть программу
            self.close()
        elif event.key() == Qt.Key_C:
            # Очистить все линии
            self.lines.clear()
            self.update()
            print("Все линии очищены")
        elif event.key() == Qt.Key_R:
            # Красный цвет
            self.pen_color = QColor(255, 0, 0, 200)
            print("Цвет изменен на красный")
        elif event.key() == Qt.Key_G:
            # Зеленый цвет
            self.pen_color = QColor(0, 255, 0, 200)
            print("Цвет изменен на зеленый")
        elif event.key() == Qt.Key_B:
            # Синий цвет
            self.pen_color = QColor(0, 0, 255, 200)
            print("Цвет изменен на синий")
        elif event.key() == Qt.Key_Y:
            # Желтый цвет
            self.pen_color = QColor(255, 255, 0, 200)
            print("Цвет изменен на желтый")
        elif event.key() == Qt.Key_1:
            # Толщина 3
            self.pen_width = 3
            print(f"Толщина линии: {self.pen_width}")
        elif event.key() == Qt.Key_2:
            # Толщина 5
            self.pen_width = 5
            print(f"Толщина линии: {self.pen_width}")
        elif event.key() == Qt.Key_3:
            # Толщина 10
            self.pen_width = 10
            print(f"Толщина линии: {self.pen_width}")
        elif event.key() == Qt.Key_4:
            # Толщина 20
            self.pen_width = 20
            print(f"Толщина линии: {self.pen_width}")


def main():
    # Создаем приложение Qt
    app = QApplication(sys.argv)

    # Создаем и показываем окно
    window = OverlayWindow()

    # Выводим подсказки в консоль
    print("\n" + "=" * 50)
    print("УПРАВЛЕНИЕ ПРОГРАММОЙ:")
    print("=" * 50)
    print("ESC - Закрыть программу")
    print("C   - Очистить все линии")
    print("R   - Красный цвет")
    print("G   - Зеленый цвет")
    print("B   - Синий цвет")
    print("Y   - Желтый цвет")
    print("1-4 - Толщина линии (3, 5, 10, 20)")
    print("=" * 50)
    print("Нажмите и удерживайте ЛКМ для рисования\n")

    # Запускаем цикл обработки событий
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
