"""
Упрощенный тест для проверки рисования
Запускайте: python test/test_drawing.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from gui.drawing_overlay import DrawingOverlay
from gui.drawing_toolbar import DrawingToolbar
import numpy as np


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧪 Тест рисования")
        self.setGeometry(100, 100, 350, 300)

        self.overlay = None
        self.toolbar = None

        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout()

        title = QLabel("🧪 Тест инструмента рисования")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        btn1 = QPushButton("🖍️ Показать оверлей")
        btn1.clicked.connect(self.show_overlay)
        btn1.setStyleSheet("padding: 10px; font-size: 14px; background-color: #4CAF50; color: white;")
        layout.addWidget(btn1)

        btn2 = QPushButton("❌ Скрыть оверлей")
        btn2.clicked.connect(self.hide_overlay)
        btn2.setStyleSheet("padding: 10px; font-size: 14px; background-color: #f44336; color: white;")
        layout.addWidget(btn2)

        btn3 = QPushButton("📸 Проверить захват")
        btn3.clicked.connect(self.check_capture)
        btn3.setStyleSheet("padding: 10px; font-size: 14px; background-color: #2196F3; color: white;")
        layout.addWidget(btn3)

        btn4 = QPushButton("🗑️ Очистить")
        btn4.clicked.connect(self.clear_drawing)
        btn4.setStyleSheet("padding: 10px; font-size: 14px;")
        layout.addWidget(btn4)

        self.info = QLabel("Статус: Ожидание")
        self.info.setAlignment(Qt.AlignCenter)
        self.info.setStyleSheet("color: #666; padding: 10px; border: 1px solid #ddd; border-radius: 5px;")
        layout.addWidget(self.info)

        widget.setLayout(layout)

    def show_overlay(self):
        if not self.overlay:
            self.overlay = DrawingOverlay()
            self.toolbar = DrawingToolbar(self.overlay)
            self.info.setText("✅ Оверлей показан. Рисуйте мышкой!")
            print("✅ Оверлей создан и показан")
        self.overlay.show()
        self.overlay.raise_()
        self.overlay.activateWindow()
        self.overlay.setFocus()
        self.toolbar.show()
        print("🖍️ Оверлей виден и активен")

    def hide_overlay(self):
        if self.overlay:
            self.overlay.hide()
            self.toolbar.hide()
            self.info.setText("❌ Оверлей скрыт")
            print("❌ Оверлей скрыт")

    def clear_drawing(self):
        if self.overlay:
            self.overlay.clear_drawing()
            self.info.setText("🗑️ Рисунки очищены")
            print("🗑️ Рисунки очищены")

    def check_capture(self):
        """Проверка захвата оверлея"""
        if not self.overlay:
            self.info.setText("❌ Сначала покажите оверлей")
            return

        print("📸 Проверка захвата...")
        arr = self.overlay.get_numpy_array()

        if arr is not None:
            max_alpha = np.max(arr[:, :, 3])
            has_drawing = np.any(arr[:, :, 3] > 10)
            print(f"✅ Захват успешен: shape={arr.shape}, max_alpha={max_alpha}, has_drawing={has_drawing}")
            self.info.setText(f"✅ Захват успешен! max_alpha={max_alpha}")

            # Сохраняем для проверки
            try:
                import cv2
                bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
                cv2.imwrite('test_capture.png', bgr)
                print("📸 Тестовое изображение сохранено как test_capture.png")
            except Exception as e:
                print(f"⚠️ Ошибка сохранения: {e}")
        else:
            print("❌ Захват не удался (нет рисунков или ошибка)")
            self.info.setText("❌ Захват не удался (нарисуйте что-нибудь)")


def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    print("=" * 60)
    print("🎨 ТЕСТ РИСОВАНИЯ")
    print("=" * 60)
    print("🖍️ 1. Нажмите 'Показать оверлей'")
    print("✏️ 2. Рисуйте мышкой на экране (должны появляться красные линии)")
    print("📸 3. Нажмите 'Проверить захват' для проверки")
    print("❌ 4. Закройте окно для выхода")
    print("=" * 60)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
