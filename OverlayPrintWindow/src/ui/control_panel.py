"""Панель управления с минималистичным интерфейсом"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QFrame, QSystemTrayIcon, QMenu
)
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QIcon, QPainter, QColor, QPixmap, QKeySequence
from PyQt5.QtWidgets import QShortcut
from src.ui.styles import PANEL_STYLE
from src.ui.mini_panel import MiniPanel
from src.utils.constants import COLORS, PANEL_WIDTH, PANEL_HEIGHT
from src.core.drawing_engine import DrawingMode


class ControlPanel(QMainWindow):
    def __init__(self, overlay):
        super().__init__()
        self.overlay = overlay

        # Настройка окна
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(PANEL_WIDTH, PANEL_HEIGHT)

        # Размещаем в правом нижнем углу
        screen = self.screen().geometry()
        self.move(
            screen.width() - PANEL_WIDTH - 20,
            screen.height() - PANEL_HEIGHT - 60
        )

        # Мини-панель
        self.mini_panel = MiniPanel(self, overlay)
        self.mini_panel.hide()
        self.is_minimized = False

        # Создаем интерфейс
        self.setup_ui()
        self.create_tray_icon()
        self.setup_shortcuts()

        # Устанавливаем стиль
        self.setStyleSheet(PANEL_STYLE)

        # Переменные для перетаскивания
        self.is_dragging = False
        self.drag_position = None

        # Таймер для обновления статуса
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)

    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        # F2 - переключение режима рисования
        shortcut_f2 = QShortcut(QKeySequence("F2"), self)
        shortcut_f2.activated.connect(self.toggle_drawing)

        # F4 - затухание
        shortcut_f4 = QShortcut(QKeySequence("F4"), self)
        shortcut_f4.activated.connect(self.toggle_fading)

        # ESC - выход из режима рисования или сворачивание
        shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        shortcut_esc.activated.connect(self.handle_escape)

        # Горячие клавиши для режимов рисования
        shortcuts = {
            "F": self.set_free_mode,
            "L": self.set_line_mode,
            "R": self.set_rectangle_mode,
            "C": self.set_circle_mode,
            "T": self.set_triangle_mode,
        }

        for key, callback in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(callback)

        # Горячие клавиши для цветов
        for i in range(1, 9):
            shortcut = QShortcut(QKeySequence(str(i)), self)
            shortcut.activated.connect(lambda checked, num=i: self.set_color_from_key(num))

    def handle_escape(self):
        """Обработка ESC"""
        if self.overlay.engine.is_active:
            self.toggle_drawing()
        elif not self.is_minimized:
            self.toggle_minimize()

    def set_free_mode(self):
        """Установить режим свободного рисования"""
        self.overlay.set_drawing_mode_type(DrawingMode.FREE)
        self.update_mode_buttons()

    def set_line_mode(self):
        """Установить режим прямой линии"""
        self.overlay.set_drawing_mode_type(DrawingMode.LINE)
        self.update_mode_buttons()

    def set_rectangle_mode(self):
        """Установить режим прямоугольника"""
        self.overlay.set_drawing_mode_type(DrawingMode.RECTANGLE)
        self.update_mode_buttons()

    def set_circle_mode(self):
        """Установить режим круга"""
        self.overlay.set_drawing_mode_type(DrawingMode.CIRCLE)
        self.update_mode_buttons()

    def set_triangle_mode(self):
        """Установить режим треугольника"""
        self.overlay.set_drawing_mode_type(DrawingMode.TRIANGLE)
        self.update_mode_buttons()

    def set_color_from_key(self, num):
        """Установить цвет по номеру клавиши"""
        colors = list(COLORS.values())
        if 1 <= num <= len(colors):
            rgb = colors[num - 1]
            color = QColor(*rgb, 255)
            self.set_color(color)
            # Обновляем мини-панель
            self.mini_panel.update_color_indicator(color)

    def setup_ui(self):
        """Создание интерфейса"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Заголовок с возможностью перетаскивания
        header = self.create_header()
        layout.addWidget(header)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: rgba(255,255,255,20); max-height: 1px;")
        layout.addWidget(line)

        # Основные кнопки
        layout.addLayout(self.create_main_buttons())

        # Режимы рисования
        layout.addWidget(self.create_mode_buttons())

        # Цвета
        layout.addWidget(self.create_color_picker())

        # Толщина
        layout.addWidget(self.create_width_control())

        # Статус
        layout.addWidget(self.create_status_bar())

        # Подсказка
        layout.addWidget(self.create_hint())

        layout.addSpacing(4)

    def create_header(self):
        """Создает заголовок панели"""
        header = QFrame()
        header.setFixedHeight(30)
        header.mousePressEvent = self.header_mouse_press
        header.mouseMoveEvent = self.header_mouse_move
        header.mouseReleaseEvent = self.header_mouse_release
        header.setCursor(Qt.PointingHandCursor)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Иконка и название
        title = QLabel("📝 Overlay Marker")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Кнопка минимизации
        mini_btn = QPushButton("━")
        mini_btn.setFixedSize(36, 36)
        mini_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 14px;
                color: rgba(255,255,255,100);
            }
            QPushButton:hover {
                color: rgba(255,255,255,200);
            }
        """)
        mini_btn.clicked.connect(self.toggle_minimize)
        header_layout.addWidget(mini_btn)

        # Кнопка закрытия
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(36, 36)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 14px;
                color: rgba(255,255,255,100);
            }
            QPushButton:hover {
                color: rgba(255,255,255,200);
            }
        """)
        close_btn.clicked.connect(self.hide)
        header_layout.addWidget(close_btn)

        return header

    def create_main_buttons(self):
        """Создает основные кнопки управления"""
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        # Кнопка рисования
        self.draw_btn = self.create_icon_button("✏️", "Рисование (F2)")
        self.draw_btn.clicked.connect(self.toggle_drawing)
        btn_layout.addWidget(self.draw_btn)

        # Кнопка очистки
        clear_btn = self.create_icon_button("🗑️", "Очистить")
        clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(clear_btn)

        # Кнопка отмены
        undo_btn = self.create_icon_button("↩️", "Отменить")
        undo_btn.clicked.connect(self.undo_last)
        btn_layout.addWidget(undo_btn)

        # Кнопка затухания
        self.fade_btn = self.create_icon_button("🌊", "Затухание (F4)")
        self.fade_btn.setCheckable(True)
        self.fade_btn.clicked.connect(self.toggle_fading)
        btn_layout.addWidget(self.fade_btn)

        return btn_layout

    def create_mode_buttons(self):
        """Создает кнопки выбора режимов рисования"""
        group = QWidget()
        layout = QHBoxLayout(group)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)

        # Кнопки режимов
        self.mode_buttons = {}
        modes = [
            ("🎨", "Свободно", DrawingMode.FREE, self.set_free_mode),
            ("📏", "Линия", DrawingMode.LINE, self.set_line_mode),
            ("⬜", "Прямоуг.", DrawingMode.RECTANGLE, self.set_rectangle_mode),
            ("⭕", "Круг", DrawingMode.CIRCLE, self.set_circle_mode),
            ("△", "Треуг.", DrawingMode.TRIANGLE, self.set_triangle_mode),
        ]

        for icon, label, mode, callback in modes:
            btn = QPushButton(icon)
            btn.setToolTip(f"{label} ({mode.name[0]})")
            btn.setFixedSize(36, 32)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(60, 60, 70, 150);
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: rgba(80, 80, 90, 200);
                }
                QPushButton:checked {
                    background: rgba(60, 130, 220, 180);
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(callback)
            self.mode_buttons[mode] = btn
            layout.addWidget(btn)

        # По умолчанию выбран свободный режим
        self.mode_buttons[DrawingMode.FREE].setChecked(True)

        return group

    def create_color_picker(self):
        """Создает палитру цветов"""
        colors_group = QWidget()
        colors_layout = QHBoxLayout(colors_group)
        colors_layout.setSpacing(5)
        colors_layout.setContentsMargins(0, 5, 0, 5)

        for i, (name, rgb) in enumerate(COLORS.items()):
            btn = QPushButton()
            btn.setFixedSize(26, 26)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});
                    border: 2px solid rgba(255,255,255,30);
                    border-radius: 13px;
                }}
                QPushButton:hover {{
                    border: 2px solid rgba(255,255,255,150);
                }}
            """)
            btn.clicked.connect(lambda checked, c=QColor(*rgb, 255): self.set_color(c))
            btn.setToolTip(f"{name} ({i+1})")
            colors_layout.addWidget(btn)

        colors_layout.addStretch()
        return colors_group

    def create_width_control(self):
        """Создает контрол толщины"""
        width_widget = QWidget()
        width_layout = QHBoxLayout(width_widget)
        width_layout.setContentsMargins(0, 5, 0, 5)
        width_layout.setSpacing(10)

        width_label = QLabel("⚪")
        width_label.setStyleSheet("font-size: 14px;")
        width_layout.addWidget(width_label)

        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setRange(1, 20)
        self.width_slider.setValue(self.overlay.engine.width)
        self.width_slider.valueChanged.connect(self.change_width)
        width_layout.addWidget(self.width_slider)

        self.width_value = QLabel(f"{self.overlay.engine.width}px")
        self.width_value.setStyleSheet("font-size: 11px; min-width: 30px;")
        width_layout.addWidget(self.width_value)

        return width_widget

    def create_status_bar(self):
        """Создает строку статуса"""
        status = QFrame()
        status.setStyleSheet("""
            background: rgba(255,255,255,10);
            border-radius: 6px;
            padding: 8px;
        """)
        status_layout = QHBoxLayout(status)
        status_layout.setContentsMargins(8, 4, 8, 4)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #666; font-size: 12px;")
        status_layout.addWidget(self.status_dot)

        self.status_text = QLabel("Обычный режим")
        self.status_text.setStyleSheet("font-size: 11px;")
        status_layout.addWidget(self.status_text)

        status_layout.addStretch()

        self.line_count = QLabel("0 линий")
        self.line_count.setStyleSheet("font-size: 11px; color: rgba(255,255,255,60);")
        status_layout.addWidget(self.line_count)

        return status

    def create_hint(self):
        """Создает подсказку о горячих клавишах"""
        hint = QLabel("F2 — рисование  |  F4 — затухание  |  F-L-R-C-T — режимы")
        hint.setStyleSheet("""
            font-size: 10px;
            color: rgba(255,255,255,40);
            text-align: center;
        """)
        hint.setAlignment(Qt.AlignCenter)
        return hint

    def create_icon_button(self, icon, tooltip):
        """Создать кнопку с иконкой"""
        btn = QPushButton(icon)
        btn.setFixedSize(44, 44)
        btn.setToolTip(tooltip)
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(60, 60, 70, 150);
                border: none;
                border-radius: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background: rgba(80, 80, 90, 200);
            }
            QPushButton:checked {
                background: rgba(220, 60, 60, 180);
            }
        """)
        btn.setCheckable(True)
        return btn

    def toggle_minimize(self):
        """Свернуть/развернуть панель"""
        self.is_minimized = not self.is_minimized

        if self.is_minimized:
            # Показываем мини-панель
            self.mini_panel.show()
            self.mini_panel.move(self.pos().x() + 10, self.pos().y() + 10)
            self.hide()
        else:
            # Показываем полную панель
            self.mini_panel.hide()
            self.show()
            self.raise_()

    def toggle_drawing(self):
        """Переключение режима рисования"""
        if not self.overlay.engine.is_active:
            self.overlay.set_drawing_mode(True)
            self.draw_btn.setChecked(True)
            self.update_ui_state(True)
        else:
            self.overlay.set_drawing_mode(False)
            self.draw_btn.setChecked(False)
            self.update_ui_state(False)
        self.update_status()
        self.mini_panel.update_state(self.overlay.engine.is_active)

    def update_ui_state(self, drawing_active: bool):
        """Обновляет состояние UI"""
        if drawing_active:
            self.draw_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(220, 60, 60, 180);
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background: rgba(240, 70, 70, 200);
                }
            """)
            self.status_dot.setStyleSheet("color: #ff4444; font-size: 12px;")
            self.status_text.setText("Рисование")
            self.tray.setToolTip("✏️ Рисование активно")
        else:
            self.draw_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(60, 60, 70, 150);
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background: rgba(80, 80, 90, 200);
                }
            """)
            self.status_dot.setStyleSheet("color: #666; font-size: 12px;")
            self.status_text.setText("Обычный режим")
            self.tray.setToolTip("✏️ Маркер поверх экрана")

    def toggle_fading(self):
        """Включить/выключить затухание"""
        enabled = self.overlay.toggle_fading()
        self.fade_btn.setChecked(enabled)
        self.fade_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba({'220, 60, 60' if enabled else '60, 60, 70'}, 180);
                border: none;
                border-radius: 10px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background: rgba({'240, 70, 70' if enabled else '80, 80, 90'}, 200);
            }}
        """)
        self.mini_panel.update_fade_state(enabled)

    def clear_all(self):
        self.overlay.clear_all()
        self.update_status()
        self.mini_panel.update_line_count(0)

    def undo_last(self):
        if self.overlay.undo():
            self.update_status()
            self.mini_panel.update_line_count(self.overlay.engine.get_line_count())

    def set_color(self, color):
        self.overlay.set_color(color)
        self.mini_panel.update_color_indicator(color)

    def change_width(self, value):
        self.overlay.set_width(value)
        self.width_value.setText(f"{value}px")
        self.mini_panel.update_width(value)

    def update_status(self):
        """Обновление статуса"""
        count = self.overlay.engine.get_line_count()
        self.line_count.setText(f"{count} линий")
        self.mini_panel.update_line_count(count)

    def update_mode_buttons(self):
        """Обновляет состояние кнопок режимов"""
        current_mode = self.overlay.engine.drawing_mode
        for mode, btn in self.mode_buttons.items():
            btn.setChecked(mode == current_mode)

    def header_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def header_mouse_move(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            # Обновляем позицию мини-панели
            if self.is_minimized:
                self.mini_panel.move(self.pos().x() + 10, self.pos().y() + 10)

    def header_mouse_release(self, event):
        self.is_dragging = False

    def create_tray_icon(self):
        """Создание иконки в трее"""
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.create_tray_icon_image())

        menu = QMenu()
        show_action = menu.addAction("Показать панель")
        show_action.triggered.connect(self.show_panel)

        menu.addSeparator()
        toggle_action = menu.addAction("Рисование (F2)")
        toggle_action.triggered.connect(self.toggle_drawing)

        menu.addSeparator()
        quit_action = menu.addAction("Выход")
        quit_action.triggered.connect(self.close_app)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_activated)
        self.tray.show()

    def show_panel(self):
        """Показать панель"""
        if self.is_minimized:
            self.toggle_minimize()
        else:
            self.show()
            self.raise_()

    def create_tray_icon_image(self):
        """Создание иконки для трея"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Круг
        painter.setBrush(QColor(40, 40, 45))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(8, 8, 48, 48)

        # Карандаш
        painter.setPen(QColor(220, 220, 220))
        painter.setBrush(QColor(220, 220, 220))
        painter.drawLine(20, 44, 44, 20)
        painter.drawLine(20, 44, 24, 48)
        painter.drawLine(44, 20, 40, 16)

        painter.end()
        return QIcon(pixmap)

    def tray_activated(self, reason):
        """Клик по иконке в трее"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_panel()

    def close_app(self):
        """Закрытие приложения"""
        try:
            if self.overlay:
                self.overlay.set_drawing_mode(False)
                self.overlay.close()
        except:
            pass
        try:
            if self.mini_panel:
                self.mini_panel.close()
        except:
            pass
        try:
            self.tray.hide()
        except:
            pass
        self.close()

    def closeEvent(self, event):
        """Закрытие - сворачиваем в трей"""
        event.ignore()
        self.hide()
        if self.is_minimized:
            self.mini_panel.hide()
        self.tray.showMessage(
            "Маркер поверх экрана",
            "Приложение в трее.\n"
            "F2 — режим рисования\n"
            "F — свободно, L — линия, R — прямоуг.\n"
            "C — круг, T — треугольник\n"
            "ESC — выход",
            QSystemTrayIcon.Information,
            3000
        )
