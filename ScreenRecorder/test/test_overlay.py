"""
Тестовый скрипт для проверки оверлея
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

from gui.drawing_overlay import DrawingOverlay
from gui.drawing_toolbar import DrawingToolbar
from core.recorder_with_overlay import RecorderWithOverlay
from core.settings import SettingsManager


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧪 Тест оверлея")
        self.setGeometry(100, 100, 350, 250)

        self.settings = SettingsManager()
        self.recorder = RecorderWithOverlay(self.settings)
        self.overlay = None
        self.toolbar = None

        # Главный виджет
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Заголовок
        title = QLabel("🧪 Тест инструмента рисования")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Кнопки
        btn1 = QPushButton("🖍️ Показать оверлей")
        btn1.clicked.connect(self.show_overlay)
        btn1.setStyleSheet("padding: 10px; font-size: 14px;")
        layout.addWidget(btn1)

        btn2 = QPushButton("❌ Скрыть оверлей")
        btn2.clicked.connect(self.hide_overlay)
        btn2.setStyleSheet("padding: 10px; font-size: 14px;")
        layout.addWidget(btn2)

        btn3 = QPushButton("▶ Начать запись")
        btn3.clicked.connect(self.start_record)
        btn3.setStyleSheet("padding: 10px; font-size: 14px; background-color: #4CAF50; color: white;")
        layout.addWidget(btn3)

        btn4 = QPushButton("⏹ Остановить запись")
        btn4.clicked.connect(self.stop_record)
        btn4.setStyleSheet("padding: 10px; font-size: 14px; background-color: #f44336; color: white;")
        layout.addWidget(btn4)

        # Информация
        self.info = QLabel("Статус: Ожидание")
        self.info.setAlignment(Qt.AlignCenter)
        self.info.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.info)

        widget.setLayout(layout)

    def show_overlay(self):
        if not self.overlay:
            self.overlay = DrawingOverlay()
            self.toolbar = DrawingToolbar(self.overlay)
            self.recorder.set_overlay_widget(self.overlay)
            self.info.setText("✅ Оверлей показан. Рисуйте мышкой!")
            print("✅ Оверлей показан")
        self.overlay.show()
        self.toolbar.show()

    def hide_overlay(self):
        if self.overlay:
            self.overlay.hide()
            self.toolbar.hide()
            self.info.setText("❌ Оверлей скрыт")
            print("❌ Оверлей скрыт")

    def start_record(self):
        self.recorder.start()
        self.info.setText("⏺ Идет запись... Рисуйте!")
        print("✅ Запись начата")

    def stop_record(self):
        self.recorder.stop()
        path = self.recorder.save()
        self.info.setText(f"✅ Запись сохранена: {os.path.basename(path)}")
        print(f"✅ Запись сохранена: {path}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())