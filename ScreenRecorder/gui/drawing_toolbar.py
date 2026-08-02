"""
Плавающая панель инструментов для рисования
"""
from PyQt5.QtWidgets import (QToolBar, QPushButton, QColorDialog,
                             QSlider, QLabel, QHBoxLayout, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class DrawingToolbar(QToolBar):
    """Плавающая панель инструментов"""
    def __init__(self, overlay, parent=None):
        super().__init__("Инструменты рисования", parent)
        self.overlay = overlay
        self.setMovable(True)
        self.setFloatable(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QToolBar {
                background-color: rgba(30, 30, 30, 230);
                border: 2px solid #007acc;
                border-radius: 10px;
                padding: 8px;
                spacing: 5px;
            }
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                min-width: 35px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
                border-color: #007acc;
            }
            QPushButton:checked {
                background-color: #d32f2f;
                border-color: #ff4444;
            }
            QPushButton.active {
                background-color: #007acc;
                border-color: #00aaff;
            }
            QLabel {
                color: #ffffff;
                padding: 0 8px;
                font-weight: bold;
            }
            QSlider {
                min-width: 100px;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #3c3c3c;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #007acc;
                width: 14px;
                height: 14px;
                border-radius: 7px;
                margin: -4px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #00aaff;
            }
        """)
        self.initUI()
        self.move(50, 50)
        print("✅ DrawingToolbar создан")

    def initUI(self):
        """Создание интерфейса панели"""
        container = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 4, 8, 4)

        # Кнопка выбора цвета
        self.color_btn = QPushButton("🎨")
        self.color_btn.setToolTip("Выбрать цвет")
        self.color_btn.clicked.connect(self.choose_color)
        self.color_btn.setStyleSheet("background-color: #ff0000;")
        layout.addWidget(self.color_btn)

        # Индикатор цвета
        self.color_indicator = QLabel()
        self.color_indicator.setFixedSize(25, 25)
        self.color_indicator.setStyleSheet("""
            background-color: #ff0000;
            border-radius: 13px;
            border: 2px solid #888;
        """)
        layout.addWidget(self.color_indicator)
        layout.addWidget(QLabel("|"))

        # Толщина кисти
        layout.addWidget(QLabel("✏️"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 20)
        self.size_slider.setValue(5)
        self.size_slider.setToolTip("Толщина кисти")
        self.size_slider.valueChanged.connect(self.on_size_changed)
        layout.addWidget(self.size_slider)
        self.size_label = QLabel("5")
        self.size_label.setFixedWidth(25)
        self.size_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.size_label)
        layout.addWidget(QLabel("|"))

        # Кнопка ластика
        self.eraser_btn = QPushButton("🧹")
        self.eraser_btn.setToolTip("Ластик")
        self.eraser_btn.setCheckable(True)
        self.eraser_btn.toggled.connect(self.toggle_eraser)
        layout.addWidget(self.eraser_btn)

        # Кнопка отмены
        self.undo_btn = QPushButton("↩️")
        self.undo_btn.setToolTip("Отменить (Ctrl+Z)")
        self.undo_btn.clicked.connect(self.overlay.undo_last)
        layout.addWidget(self.undo_btn)

        # Кнопка очистки
        self.clear_btn = QPushButton("🗑️")
        self.clear_btn.setToolTip("Очистить все")
        self.clear_btn.clicked.connect(self.overlay.clear_drawing)
        layout.addWidget(self.clear_btn)
        layout.addWidget(QLabel("|"))

        # Кнопка скрыть
        self.hide_btn = QPushButton("✖")
        self.hide_btn.setToolTip("Скрыть панель")
        self.hide_btn.clicked.connect(self.hide)
        self.hide_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                border-color: #ff4444;
            }
            QPushButton:hover {
                background-color: #ff4444;
            }
        """)
        layout.addWidget(self.hide_btn)

        container.setLayout(layout)
        self.addWidget(container)

    def choose_color(self):
        """Выбор цвета"""
        color = QColorDialog.getColor(self.overlay.pen_color, self, "Выберите цвет")
        if color.isValid():
            self.overlay.set_color(color)
            # Обновляем индикатор
            self.color_indicator.setStyleSheet(f"""
                background-color: {color.name()};
                border-radius: 13px;
                border: 2px solid #888;
            """)
            self.color_btn.setStyleSheet(f"background-color: {color.name()};")
            # Если ластик активен, отключаем
            if self.eraser_btn.isChecked():
                self.eraser_btn.setChecked(False)
                self.overlay.toggle_eraser(False)

    def on_size_changed(self, value):
        """Изменение толщины"""
        self.size_label.setText(str(value))
        self.overlay.set_width(value)

    def toggle_eraser(self, checked):
        """Включение/выключение ластика"""
        self.overlay.toggle_eraser(checked)

    def keyPressEvent(self, event):
        """Обработка клавиш"""
        if event.key() == Qt.Key_Escape:
            self.hide()
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            self.overlay.undo_last()
        elif event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            self.overlay.clear_drawing()
        else:
            super().keyPressEvent(event)
