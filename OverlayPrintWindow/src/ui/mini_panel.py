"""Мини-панель управления с основными функциями"""
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSlider
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor

class MiniPanel(QMainWindow):
    def __init__(self, parent, overlay):
        super().__init__(parent)
        self.parent_panel = parent
        self.overlay = overlay

        # Настройка окна
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(180, 45)

        # Создаем интерфейс
        self.setup_ui()

        # Для перетаскивания
        self.is_dragging = False
        self.drag_position = None

        # Стиль
        self.setStyleSheet("""
            QMainWindow {
                background: rgba(20, 20, 25, 240);
                border-radius: 22px;
                border: 1px solid rgba(255, 255, 255, 20);
            }
            QWidget {
                background: transparent;
                color: #e0e0e0;
            }
            QPushButton {
                background: rgba(60, 60, 70, 150);
                border: none;
                border-radius: 6px;
                font-size: 12px;
                padding: 4px;
            }
            QPushButton:hover {
                background: rgba(80, 80, 90, 200);
            }
            QPushButton:checked {
                background: rgba(220, 60, 60, 180);
            }
        """)

    def setup_ui(self):
        """Создание интерфейса мини-панели"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # Кнопка рисования
        self.draw_btn = QPushButton("✏️")
        self.draw_btn.setFixedSize(32, 32)
        self.draw_btn.setToolTip("Рисование (F2)")
        self.draw_btn.clicked.connect(self.parent_panel.toggle_drawing)
        layout.addWidget(self.draw_btn)

        # Индикатор цвета
        self.color_indicator = QFrame()
        self.color_indicator.setFixedSize(20, 20)
        self.color_indicator.setStyleSheet("""
            border-radius: 10px;
            border: 2px solid rgba(255,255,255,50);
        """)
        self.update_color_indicator(self.overlay.engine.color)
        layout.addWidget(self.color_indicator)

        # Индикатор толщины
        self.width_label = QLabel(f"{self.overlay.engine.width}")
        self.width_label.setFixedSize(20, 20)
        self.width_label.setAlignment(Qt.AlignCenter)
        self.width_label.setStyleSheet("""
            font-size: 10px;
            font-weight: bold;
            border-radius: 10px;
            background: rgba(255,255,255,10);
        """)
        layout.addWidget(self.width_label)

        # Кнопка затухания
        self.fade_btn = QPushButton("🌊")
        self.fade_btn.setFixedSize(32, 32)
        self.fade_btn.setToolTip("Затухание (F4)")
        self.fade_btn.setCheckable(True)
        self.fade_btn.clicked.connect(self.parent_panel.toggle_fading)
        layout.addWidget(self.fade_btn)

        # Счетчик линий
        self.line_count_label = QLabel("0")
        self.line_count_label.setFixedSize(20, 20)
        self.line_count_label.setAlignment(Qt.AlignCenter)
        self.line_count_label.setStyleSheet("""
            font-size: 10px;
            background: rgba(255,255,255,10);
            border-radius: 10px;
        """)
        layout.addWidget(self.line_count_label)

        # Кнопка развернуть
        expand_btn = QPushButton("↗")
        expand_btn.setFixedSize(24, 24)
        expand_btn.setToolTip("Развернуть панель")
        expand_btn.clicked.connect(self.parent_panel.toggle_minimize)
        layout.addWidget(expand_btn)

    def update_color_indicator(self, color: QColor):
        """Обновляет индикатор цвета"""
        self.color_indicator.setStyleSheet(f"""
            border-radius: 10px;
            border: 2px solid rgba(255,255,255,50);
            background: rgb({color.red()}, {color.green()}, {color.blue()});
        """)

    def update_width(self, width: int):
        """Обновляет индикатор толщины"""
        self.width_label.setText(str(width))

    def update_line_count(self, count: int):
        """Обновляет счетчик линий"""
        self.line_count_label.setText(str(count))

    def update_state(self, drawing_active: bool):
        """Обновляет состояние кнопки рисования"""
        self.draw_btn.setChecked(drawing_active)
        self.draw_btn.setStyleSheet("""
            QPushButton {
                background: rgba(220, 60, 60, 180);
                border: none;
                border-radius: 6px;
                font-size: 12px;
                padding: 4px;
            }
            QPushButton:hover {
                background: rgba(240, 70, 70, 200);
            }
        """ if drawing_active else """
            QPushButton {
                background: rgba(60, 60, 70, 150);
                border: none;
                border-radius: 6px;
                font-size: 12px;
                padding: 4px;
            }
            QPushButton:hover {
                background: rgba(80, 80, 90, 200);
            }
        """)

    def update_fade_state(self, enabled: bool):
        """Обновляет состояние кнопки затухания"""
        self.fade_btn.setChecked(enabled)
        self.fade_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba({'220, 60, 60' if enabled else '60, 60, 70'}, 180);
                border: none;
                border-radius: 6px;
                font-size: 12px;
                padding: 4px;
            }}
            QPushButton:hover {{
                background: rgba({'240, 70, 70' if enabled else '80, 80, 90'}, 200);
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            # Обновляем позицию родительской панели
            if self.parent_panel.is_minimized:
                self.parent_panel.move(self.pos().x() - 10, self.pos().y() - 10)

    def mouseReleaseEvent(self, event):
        self.is_dragging = False
