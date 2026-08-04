from PyQt5.QtWidgets import QWidget, QDesktopWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor
from pynput import mouse
import threading
import sys


class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Настройка флагов окна - делаем окно прозрачным для кликов
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        # Настройка прозрачности
        self.setAttribute(Qt.WA_TranslucentBackground)
        # ВАЖНО: Не используем WA_TransparentForMouseEvents,
        # чтобы окно получало события мыши

        # Установка размера на весь экран
        screen_geometry = QDesktopWidget().screenGeometry()
        self.setGeometry(screen_geometry)

        # Переменные для рисования
        self.drawing = False
        self.lines = []
        self.current_line = []
        self.history = []

        # Режимы работы
        self.is_drawing_mode = False  # Режим рисования включен/выключен
        self.is_paused = False

        # Настройки пера
        self.pen_color = QColor(255, 0, 0, 255)
        self.pen_width = 8

        self.setCursor(Qt.ArrowCursor)
        self.showFullScreen()

        # Запускаем глобальный слушатель мыши
        self.start_mouse_listener()

        print("=" * 60)
        print("🎨 МАРКЕР ПОВЕРХ ЭКРАНА")
        print("=" * 60)
        print("📌 Нажмите F2 для входа в режим рисования")
        print("📌 Нажмите F2 для выхода из режима рисования")
        print("📌 Нажмите F1 для справки")
        print("=" * 60)

    def start_mouse_listener(self):
        """Запускает глобальный слушатель мыши"""

        def on_click(x, y, button, pressed):
            # Игнорируем если не в режиме рисования
            if not self.is_drawing_mode:
                return

            if button == mouse.Button.left:
                if pressed and not self.is_paused:
                    # Начало рисования
                    self.drawing = True
                    local_pos = self.mapFromGlobal(QPoint(x, y))
                    self.current_line = [local_pos]
                    print(f"🖱️ Рисование: ({local_pos.x()}, {local_pos.y()})")
                elif not pressed and self.drawing:
                    # Конец рисования
                    self.drawing = False
                    if len(self.current_line) > 1:
                        self.history.append(self.lines.copy())
                        self.lines.append(self.current_line)
                        print(f"✅ Линия сохранена. Всего: {len(self.lines)}")
                    self.current_line = []
                    self.update()

        def on_move(x, y):
            # Игнорируем если не в режиме рисования
            if not self.is_drawing_mode:
                return

            if self.drawing and not self.is_paused:
                local_pos = self.mapFromGlobal(QPoint(x, y))
                if 0 <= local_pos.x() <= self.width() and 0 <= local_pos.y() <= self.height():
                    self.current_line.append(local_pos)
                    self.update()

        # Запускаем слушатель в отдельном потоке
        listener = mouse.Listener(on_click=on_click, on_move=on_move)
        listener.daemon = True
        listener.start()
        print("✅ Глобальный слушатель мыши запущен")

    def toggle_drawing_mode(self):
        """Включить/выключить режим рисования"""
        self.is_drawing_mode = not self.is_drawing_mode

        if self.is_drawing_mode:
            self.setCursor(Qt.CrossCursor)
            # Делаем окно непрозрачным для событий мыши
            # Теперь все клики будут перехватываться нашим окном
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            print("🟢 РЕЖИМ РИСОВАНИЯ ВКЛЮЧЕН")
            print("   🖱️ Нажмите и удерживайте ЛКМ для рисования")
            print("   ⌨️ F2 - выход, F3 - пауза")
        else:
            self.setCursor(Qt.ArrowCursor)
            self.drawing = False
            self.current_line = []
            # Делаем окно прозрачным для событий мыши
            # Клики проходят сквозь к приложениям под ним
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            print("🔴 РЕЖИМ РИСОВАНИЯ ВЫКЛЮЧЕН")
            print("   Мышь работает в обычном режиме")

        self.update()

    def toggle_pause(self):
        """Пауза/возобновление рисования"""
        if not self.is_drawing_mode:
            print("⚠️ Сначала включите режим рисования (F2)")
            return

        self.is_paused = not self.is_paused
        status = "ПАУЗА" if self.is_paused else "ВОЗОБНОВЛЕНО"
        print(f"⏸️ Рисование: {status}")
        if self.is_paused:
            self.drawing = False
            self.current_line = []
        self.update()

    def paintEvent(self, event):
        """Отрисовка всех линий"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Полностью прозрачный фон
        painter.setBrush(Qt.transparent)
        painter.drawRect(self.rect())

        # Если режим паузы - рисуем затемнение
        if self.is_paused and self.is_drawing_mode:
            painter.setBrush(QColor(0, 0, 0, 80))
            painter.drawRect(self.rect())
            painter.setPen(QColor(255, 255, 255, 200))
            font = painter.font()
            font.setPointSize(48)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "⏸ ПАУЗА")

        # Настраиваем перо
        if self.is_drawing_mode and not self.is_paused:
            pen = QPen(
                self.pen_color,
                self.pen_width,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin
            )
        else:
            pen = QPen(
                QColor(128, 128, 128, 50),
                self.pen_width,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin
            )
        painter.setPen(pen)

        # Рисуем все сохраненные линии
        for line in self.lines:
            if len(line) > 1:
                for i in range(len(line) - 1):
                    painter.drawLine(line[i], line[i + 1])

        # Рисуем текущую линию
        if len(self.current_line) > 1:
            for i in range(len(self.current_line) - 1):
                painter.drawLine(self.current_line[i], self.current_line[i + 1])

        # Индикатор состояния
        self.draw_status_indicator(painter)

    def draw_status_indicator(self, painter):
        """Рисует индикатор состояния"""
        # Фон индикатора
        painter.setBrush(QColor(0, 0, 0, 200))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.width() - 220, 10, 200, 70, 10, 10)

        # Текст статуса
        painter.setPen(QColor(255, 255, 255, 200))
        font = painter.font()
        font.setPointSize(11)
        painter.setFont(font)

        if self.is_drawing_mode:
            if self.is_paused:
                mode = "⏸ ПАУЗА"
                color = QColor(255, 255, 0)
            else:
                mode = "🟢 РИСОВАНИЕ"
                color = QColor(0, 255, 0)
        else:
            mode = "⚪ ОБЫЧНЫЙ"
            color = QColor(128, 128, 128)

        painter.setPen(color)
        painter.drawText(self.width() - 210, 32, mode)

        # Дополнительная информация
        painter.setPen(QColor(200, 200, 200, 150))
        font.setPointSize(9)
        painter.setFont(font)
        info = f"Цв: {self.get_color_name()} | Толщ: {self.pen_width}px"
        painter.drawText(self.width() - 210, 48, info)

        # Подсказка
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QColor(150, 150, 150, 150))
        if self.is_drawing_mode:
            hint = "F2 - Выйти | F3 - Пауза"
        else:
            hint = "F2 - Войти в режим рисования"
        painter.drawText(self.width() - 210, 65, hint)

    def get_color_name(self):
        """Возвращает название текущего цвета"""
        colors = {
            (255, 0, 0): "Красный",
            (0, 255, 0): "Зеленый",
            (0, 0, 255): "Синий",
            (255, 255, 0): "Желтый",
            (255, 0, 255): "Розовый",
            (255, 165, 0): "Оранжевый",
            (255, 255, 255): "Белый"
        }
        rgb = (self.pen_color.red(), self.pen_color.green(), self.pen_color.blue())
        return colors.get(rgb, "Другой")

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        key = event.key()
        modifiers = event.modifiers()

        # Выход
        if key == Qt.Key_Escape:
            if self.is_drawing_mode:
                self.toggle_drawing_mode()
            else:
                self.close()

        # Справка
        elif key == Qt.Key_F1:
            self.show_help()

        # Включить/выключить режим рисования
        elif key == Qt.Key_F2:
            self.toggle_drawing_mode()

        # Пауза
        elif key == Qt.Key_F3:
            self.toggle_pause()

        # Очистка
        elif key == Qt.Key_C:
            self.clear_all()

        # Отмена (Ctrl+Z)
        elif key == Qt.Key_Z and modifiers & Qt.ControlModifier:
            self.undo_last()

        # Смена цвета (только в режиме рисования)
        elif self.is_drawing_mode:
            if key == Qt.Key_R:
                self.change_color(QColor(255, 0, 0, 255), "Красный")
            elif key == Qt.Key_G:
                self.change_color(QColor(0, 255, 0, 255), "Зеленый")
            elif key == Qt.Key_B:
                self.change_color(QColor(0, 0, 255, 255), "Синий")
            elif key == Qt.Key_Y:
                self.change_color(QColor(255, 255, 0, 255), "Желтый")
            elif key == Qt.Key_P:
                self.change_color(QColor(255, 0, 255, 255), "Розовый")
            elif key == Qt.Key_O:
                self.change_color(QColor(255, 165, 0, 255), "Оранжевый")
            elif key == Qt.Key_W:
                self.change_color(QColor(255, 255, 255, 255), "Белый")
            elif key == Qt.Key_1:
                self.change_width(3)
            elif key == Qt.Key_2:
                self.change_width(5)
            elif key == Qt.Key_3:
                self.change_width(10)
            elif key == Qt.Key_4:
                self.change_width(15)
            elif key == Qt.Key_5:
                self.change_width(25)

        # Передаем в контроллер
        elif hasattr(self, 'controller'):
            self.controller.handle_key_press(event)

    def clear_all(self):
        """Очистка всех линий"""
        if self.lines:
            self.history.append(self.lines.copy())
        self.lines.clear()
        self.current_line.clear()
        self.update()
        print("🗑️ Все линии очищены")

    def undo_last(self):
        """Отмена последней линии"""
        if self.lines:
            removed = self.lines.pop()
            print(f"↩️ Отменено: удалена последняя линия. Осталось: {len(self.lines)}")
            self.update()
        else:
            print("ℹ️ Нет линий для отмены")

    def change_color(self, color, name):
        """Смена цвета"""
        self.pen_color = color
        print(f"🎨 Цвет изменен на {name}")

    def change_width(self, width):
        """Изменение толщины"""
        self.pen_width = width
        print(f"📏 Толщина линии: {width}px")

    def show_help(self):
        """Показать справку"""
        help_text = """
        ═══════════════════════════════════════════════════════════
        📖 УПРАВЛЕНИЕ ПРОГРАММОЙ
        ═══════════════════════════════════════════════════════════

        РЕЖИМЫ РАБОТЫ:
        F2      - Вход/выход из режима рисования
        F3      - Пауза/возобновление (в режиме рисования)
        ESC     - Выход из режима рисования или закрытие

        В РЕЖИМЕ РИСОВАНИЯ:
        🖱️ Все клики перехватываются для рисования
        🔓 Приложения под окном НЕ получают события мыши

        ЛКМ     - Начать/продолжить рисование
        Отпустить ЛКМ - Завершить линию
        C       - Очистить все линии
        Ctrl+Z  - Отменить последнюю линию

        ЦВЕТА (в режиме рисования):
        R - Красный    G - Зеленый    B - Синий
        Y - Желтый     P - Розовый    O - Оранжевый
        W - Белый

        ТОЛЩИНА (в режиме рисования):
        1 - 3px    2 - 5px    3 - 10px
        4 - 15px   5 - 25px

        💡 В обычном режиме мышь работает как обычно
        ═══════════════════════════════════════════════════════════
        """
        print(help_text)

    def set_controller(self, controller):
        """Установка контроллера"""
        self.controller = controller

    def closeEvent(self, event):
        """Закрытие окна"""
        super().closeEvent(event)