"""Панель управления с минималистичным интерфейсом"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QColorDialog, QFrame,
    QSystemTrayIcon, QMenu
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPainter, QColor, QPixmap, QKeySequence
from PyQt5.QtWidgets import QShortcut
from src.ui.styles import PANEL_STYLE
from src.utils.constants import PANEL_WIDTH, PANEL_HEIGHT, COLORS


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

        # Создаем интерфейс
        self.setup_ui()
        self.create_tray_icon()
        self.setup_shortcuts()

        # Устанавливаем стиль
        self.setStyleSheet(PANEL_STYLE)

        # Переменные
        self.is_dragging = False
        self.drag_position = None

    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        # F2 - переключение режима рисования
        shortcut_f2 = QShortcut(QKeySequence("F2"), self)
        shortcut_f2.activated.connect(self.toggle_drawing)

        # ESC - выход из режима рисования или сворачивание
        shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        shortcut_esc.activated.connect(self.handle_escape)

    def handle_escape(self):
        """Обработка ESC"""
        if self.overlay.engine.is_active:
            self.toggle_drawing()
        else:
            self.hide()

    def setup_ui(self):
        """Создание интерфейса"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Заголовок с возможностью перетаскивания
        header = QFrame()
        header.setFixedHeight(30)
        header.mousePressEvent = self.header_mouse_press
        header.mouseMoveEvent = self.header_mouse_move
        header.setCursor(Qt.PointingHandCursor)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Иконка и название
        title = QLabel("✏️")
        title.setStyleSheet("font-size: 16px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Кнопка закрытия
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
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

        layout.addWidget(header)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: rgba(255,255,255,20); max-height: 1px;")
        layout.addWidget(line)

        # Основные кнопки
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

        layout.addLayout(btn_layout)

        # Цвета
        colors_group = QWidget()
        colors_layout = QHBoxLayout(colors_group)
        colors_layout.setSpacing(6)
        colors_layout.setContentsMargins(0, 5, 0, 5)

        for name, rgb in COLORS.items():
            btn = QPushButton()
            btn.setFixedSize(28, 28)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});
                    border: 2px solid rgba(255,255,255,30);
                    border-radius: 14px;
                }}
                QPushButton:hover {{
                    border: 2px solid rgba(255,255,255,150);
                }}
            """)
            btn.clicked.connect(lambda checked, c=QColor(*rgb, 255): self.set_color(c))
            colors_layout.addWidget(btn)

        colors_layout.addStretch()
        layout.addWidget(colors_group)

        # Толщина
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

        layout.addWidget(width_widget)

        # Статус
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

        layout.addWidget(status)

        # Подсказка о горячих клавишах
        hint = QLabel("F2 — рисование  |  ESC — выход")
        hint.setStyleSheet("""
            font-size: 10px; 
            color: rgba(255,255,255,40);
            text-align: center;
        """)
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        layout.addSpacing(4)

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

    def create_tray_icon(self):
        """Создание иконки в трее"""
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.create_tray_icon_image())

        menu = QMenu()

        show_action = menu.addAction("Показать панель")
        show_action.triggered.connect(self.show)

        menu.addSeparator()

        toggle_action = menu.addAction("Рисование (F2)")
        toggle_action.triggered.connect(self.toggle_drawing)

        menu.addSeparator()

        quit_action = menu.addAction("Выход")
        quit_action.triggered.connect(self.close_app)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_activated)
        self.tray.show()

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

    def toggle_drawing(self):
        """Переключение режима рисования"""
        if not self.overlay.engine.is_active:
            self.overlay.set_drawing_mode(True)
            self.draw_btn.setChecked(True)
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
            self.overlay.set_drawing_mode(False)
            self.draw_btn.setChecked(False)
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

        self.update_status()

    def clear_all(self):
        """Очистка"""
        self.overlay.clear_all()
        self.update_status()

    def undo_last(self):
        """Отмена"""
        if self.overlay.undo():
            self.update_status()

    def set_color(self, color):
        """Установка цвета"""
        self.overlay.set_color(color)

    def change_width(self, value):
        """Изменение толщины"""
        self.overlay.set_width(value)
        self.width_value.setText(f"{value}px")

    def update_status(self):
        """Обновление статуса"""
        count = self.overlay.engine.get_line_count()
        self.line_count.setText(f"{count} линий")

    def header_mouse_press(self, event):
        """Начало перетаскивания"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def header_mouse_move(self, event):
        """Перетаскивание"""
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_position)

    def header_mouse_release(self, event):
        """Конец перетаскивания"""
        self.is_dragging = False

    def tray_activated(self, reason):
        """Клик по иконке в трее"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()

    def close_app(self):
        """Закрытие приложения"""
        self.overlay.set_drawing_mode(False)
        self.overlay.close()
        self.tray.hide()
        self.close()

    def closeEvent(self, event):
        """Закрытие - сворачиваем в трей"""
        event.ignore()
        self.hide()
        self.tray.showMessage(
            "Маркер поверх экрана",
            "Приложение в трее.\nF2 — режим рисования\nESC — выход",
            QSystemTrayIcon.Information,
            3000
        )
