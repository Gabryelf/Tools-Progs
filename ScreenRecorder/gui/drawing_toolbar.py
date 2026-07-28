"""
Плавающая панель инструментов для рисования
"""

from PyQt5.QtWidgets import (QToolBar, QPushButton, QColorDialog,
                             QSlider, QLabel, QHBoxLayout, QWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPixmap


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
                background-color: rgba(30, 30, 30, 200);
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 5px;
                spacing: 3px;
            }
            QPushButton {
                background-color: transparent;
                color: #d4d4d4;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 14px;
                min-width: 30px;
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 60, 150);
                border-color: #3c3c3c;
            }
            QPushButton.active {
                background-color: #007acc;
                color: white;
            }
            QLabel {
                color: #d4d4d4;
                padding: 0 5px;
            }
            QSlider {
                min-width: 80px;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #3c3c3c;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #007acc;
                width: 12px;
                height: 12px;
                border-radius: 6px;
                margin: -4px 0;
            }
        """)

        self.initUI()

        # Позиция по умолчанию
        self.move(50, 50)

    def initUI(self):
        """Создание интерфейса панели"""

        # Контейнер для виджетов
        container = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 2, 5, 2)

        # Кнопка выбора цвета
        self.color_btn = QPushButton("🎨")
        self.color_btn.setToolTip("Выбрать цвет")
        self.color_btn.clicked.connect(self.choose_color)
        layout.addWidget(self.color_btn)

        # Индикатор цвета
        self.color_indicator = QLabel()
        self.color_indicator.setFixedSize(20, 20)
        self.color_indicator.setStyleSheet("""
            background-color: rgba(255, 50, 50, 200);
            border-radius: 10px;
            border: 1px solid #666;
        """)
        layout.addWidget(self.color_indicator)

        # Разделитель
        layout.addWidget(QLabel("|"))

        # Толщина кисти
        layout.addWidget(QLabel("✏️"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 20)
        self.size_slider.setValue(4)
        self.size_slider.setToolTip("Толщина кисти")
        self.size_slider.valueChanged.connect(self.on_size_changed)
        layout.addWidget(self.size_slider)

        self.size_label = QLabel("4")
        self.size_label.setFixedWidth(20)
        layout.addWidget(self.size_label)

        # Разделитель
        layout.addWidget(QLabel("|"))

        # Кнопка ластика
        self.eraser_btn = QPushButton("🧹")
        self.eraser_btn.setToolTip("Ластик (стирает рисунки)")
        self.eraser_btn.setCheckable(True)
        self.eraser_btn.toggled.connect(self.toggle_eraser)
        layout.addWidget(self.eraser_btn)

        # Кнопка отмены
        self.undo_btn = QPushButton("↩️")
        self.undo_btn.setToolTip("Отменить последнее действие")
        self.undo_btn.clicked.connect(self.overlay.undo_last)
        layout.addWidget(self.undo_btn)

        # Кнопка очистки
        self.clear_btn = QPushButton("🗑️")
        self.clear_btn.setToolTip("Очистить все")
        self.clear_btn.clicked.connect(self.overlay.clear_drawing)
        layout.addWidget(self.clear_btn)

        # Разделитель
        layout.addWidget(QLabel("|"))

        # Кнопка скрыть
        self.hide_btn = QPushButton("❌")
        self.hide_btn.setToolTip("Скрыть панель")
        self.hide_btn.clicked.connect(self.hide)
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
                background-color: rgba({color.red()}, {color.green()}, {color.blue()}, 200);
                border-radius: 10px;
                border: 1px solid #666;
            """)
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
        if checked:
            self.eraser_btn.setStyleSheet("background-color: #d32f2f; color: white;")
        else:
            self.eraser_btn.setStyleSheet("")

    def showEvent(self, event):
        """При показе обновляем позицию"""
        super().showEvent(event)
        # Автоматически скрываем через 5 секунд бездействия
        # (можно добавить таймер)

    def keyPressEvent(self, event):
        """Обработка клавиш"""
        if event.key() == Qt.Key_Escape:
            self.hide()
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            self.overlay.undo_last()
        elif event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            self.overlay.clear_drawing()
