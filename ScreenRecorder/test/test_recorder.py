"""
Тестовый модуль для проверки записи экрана и звука
"""
import sys
import os
import time
import logging
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer

from core import ScreenRecorder, SettingsManager


def setup_test_logging():
    """Настройка логирования для тестов"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


class RecorderTestWindow(QMainWindow):
    """Тестовое окно для проверки записи"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧪 Тест записи экрана")
        self.setGeometry(100, 100, 400, 350)

        self.settings = SettingsManager()
        self.recorder = ScreenRecorder(self.settings)

        self.initUI()
        self.start_time = None
        self.frames_count = 0

    def initUI(self):
        """Инициализация интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Заголовок
        title = QLabel("🧪 Тест записи экрана")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Информация
        self.status_label = QLabel("✅ Готов к записи")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 15px; border: 1px solid #ccc; border-radius: 5px;")
        layout.addWidget(self.status_label)

        # Информация о записи
        self.info_label = QLabel("⏱ 00:00:00 | 📹 0 кадров")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.info_label)

        # Кнопки
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ Начать запись (5 сек)")
        self.start_btn.clicked.connect(self.start_recording)
        self.start_btn.setStyleSheet("padding: 10px; background-color: #4CAF50; color: white; font-weight: bold;")
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹ Остановить")
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("padding: 10px; background-color: #f44336; color: white; font-weight: bold;")
        btn_layout.addWidget(self.stop_btn)

        layout.addLayout(btn_layout)

        # Кнопка теста сохранения
        self.test_save_btn = QPushButton("💾 Тест сохранения")
        self.test_save_btn.clicked.connect(self.test_save)
        self.test_save_btn.setStyleSheet("padding: 10px; background-color: #2196F3; color: white; font-weight: bold;")
        layout.addWidget(self.test_save_btn)

        # Автоматическая остановка через 5 секунд
        self.auto_stop_timer = QTimer()
        self.auto_stop_timer.setSingleShot(True)
        self.auto_stop_timer.timeout.connect(self.auto_stop_recording)

    def start_recording(self):
        """Начать запись"""
        if self.recorder.is_recording:
            return

        print("\n" + "=" * 60)
        print("🎬 НАЧАЛО ЗАПИСИ")
        print("=" * 60)

        self.recorder.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("⏺ ИДЕТ ЗАПИСЬ...")
        self.status_label.setStyleSheet(
            "padding: 15px; border: 1px solid #f44336; border-radius: 5px; color: #f44336; font-weight: bold;")

        self.start_time = time.time()
        self.frames_count = 0

        # Автоматическая остановка через 5 секунд
        self.auto_stop_timer.start(5000)
        print("⏱ Автоматическая остановка через 5 секунд")

    def stop_recording(self):
        """Остановить запись"""
        if not self.recorder.is_recording:
            return

        print("\n" + "=" * 60)
        print("⏹ ОСТАНОВКА ЗАПИСИ")
        print("=" * 60)

        self.auto_stop_timer.stop()
        self.recorder.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def auto_stop_recording(self):
        """Автоматическая остановка"""
        print("⏱ Автоматическая остановка...")
        self.stop_recording()

    def on_start(self):
        """Колбэк начала записи"""
        print("✅ Запись начата")
        print(f"   - FPS: {self.settings.get('video_fps')}")
        print(f"   - Запись звука: {'да' if self.settings.get('record_audio') else 'нет'}")

    def on_stop(self):
        """Колбэк остановки записи"""
        duration = time.time() - self.start_time if self.start_time else 0
        print(f"\n✅ Запись остановлена")
        print(f"   - Длительность: {duration:.1f} сек")
        print(f"   - Кадров: {self.frames_count}")
        print(f"   - Средний FPS: {self.frames_count / duration if duration > 0 else 0:.1f}")

        self.status_label.setText("✅ Запись остановлена")
        self.status_label.setStyleSheet(
            "padding: 15px; border: 1px solid #4CAF50; border-radius: 5px; color: #4CAF50; font-weight: bold;")

    def on_error(self, error):
        """Колбэк ошибки"""
        print(f"❌ Ошибка: {error}")
        self.status_label.setText(f"❌ Ошибка: {error}")
        self.status_label.setStyleSheet(
            "padding: 15px; border: 1px solid #f44336; border-radius: 5px; color: #f44336; font-weight: bold;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def on_progress(self, data):
        """Колбэк прогресса"""
        self.frames_count = data['frames']
        duration = data['duration']

        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        self.info_label.setText(f"⏱ {time_str} | 📹 {data['frames']} кадров | FPS: {data['fps']:.1f}")

        # Выводим в консоль раз в 2 секунды
        if int(duration) % 2 == 0:
            print(f"   Прогресс: {time_str}, кадров: {data['frames']}, FPS: {data['fps']:.1f}")

    def test_save(self):
        """Тест сохранения"""
        print("\n" + "=" * 60)
        print("💾 ТЕСТ СОХРАНЕНИЯ")
        print("=" * 60)

        if not self.recorder.temp_files:
            print("❌ Нет данных для сохранения. Сначала сделайте запись.")
            return

        try:
            # Сохраняем с уникальным именем
            timestamp = time.strftime("%Y-%d-%m_%H-%M-%S")
            test_output = f"test_recording_{timestamp}.mp4"

            print(f"   Сохранение в: {test_output}")
            output_path = self.recorder.save(test_output)

            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                size_mb = size / (1024 * 1024)
                print(f"✅ Файл сохранен успешно!")
                print(f"   - Путь: {output_path}")
                print(f"   - Размер: {size_mb:.2f} MB")

                self.status_label.setText(f"✅ Сохранено: {os.path.basename(output_path)} ({size_mb:.1f} MB)")
                self.status_label.setStyleSheet(
                    "padding: 15px; border: 1px solid #4CAF50; border-radius: 5px; color: #4CAF50; font-weight: bold;")
            else:
                print("❌ Файл не создан")

        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            self.status_label.setText(f"❌ Ошибка: {e}")
            self.status_label.setStyleSheet(
                "padding: 15px; border: 1px solid #f44336; border-radius: 5px; color: #f44336; font-weight: bold;")


def test_recorder_components():
    """Тестирование компонентов рекордера"""
    print("\n" + "=" * 60)
    print("🔧 ТЕСТИРОВАНИЕ КОМПОНЕНТОВ")
    print("=" * 60)

    settings = SettingsManager()

    # 1. Тест настроек
    print("\n📋 Настройки:")
    print(f"   - Запись звука: {settings.get('record_audio')}")
    print(f"   - Шумоподавление: {settings.get('noise_reduction')}")
    print(f"   - FPS: {settings.get('video_fps')}")
    print(f"   - Частота аудио: {settings.get('audio_sample_rate')}")
    print(f"   - Папка сохранения: {settings.get('save_path')}")

    # 2. Тест создания рекордера
    print("\n🎬 Создание рекордера...")
    recorder = ScreenRecorder(settings)
    print("✅ Рекордер создан")
    print(f"   - Состояние: {'запись' if recorder.is_recording else 'ожидание'}")
    print(f"   - Временная папка: {recorder._temp_dir}")

    # 3. Тест аудио устройств
    print("\n🎵 Проверка аудио устройств...")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [i for i, d in enumerate(devices) if d['max_input_channels'] > 0]
        print(f"   - Найдено входных устройств: {len(input_devices)}")
        if input_devices:
            for i in input_devices[:3]:  # Показываем первые 3
                print(f"     [{i}] {devices[i]['name']}")
    except Exception as e:
        print(f"   ⚠️ Ошибка: {e}")

    # 4. Тест импорта moviepy
    print("\n📦 Проверка зависимостей:")
    try:
        from moviepy.editor import VideoFileClip
        print("   ✅ moviepy доступен")
    except ImportError:
        print("   ❌ moviepy не установлен (сохранение будет только видео)")

    try:
        import cv2
        print(f"   ✅ OpenCV доступен (версия: {cv2.__version__})")
    except ImportError:
        print("   ❌ OpenCV не установлен")

    try:
        import numpy as np
        print(f"   ✅ NumPy доступен (версия: {np.__version__})")
    except ImportError:
        print("   ❌ NumPy не установлен")

    print("\n✅ Тестирование компонентов завершено")


def main():
    """Главная функция тестирования"""
    setup_test_logging()

    print("\n" + "=" * 60)
    print("🎬 ТЕСТИРОВАНИЕ ЗАПИСИ ЭКРАНА")
    print("=" * 60)

    # Сначала тестируем компоненты
    test_recorder_components()

    # Затем запускаем GUI тест
    app = QApplication(sys.argv)
    window = RecorderTestWindow()
    window.show()

    print("\n" + "=" * 60)
    print("🔍 ИНСТРУКЦИЯ ПО ТЕСТИРОВАНИЮ")
    print("=" * 60)
    print("1. Нажмите 'Начать запись (5 сек)' - запись автоматически остановится через 5 секунд")
    print("2. Или нажмите 'Остановить' для ручной остановки")
    print("3. После остановки нажмите 'Тест сохранения' для сохранения файла")
    print("4. Проверьте сохраненный файл")
    print("=" * 60)
    print("\n💡 Совет: Во время записи попробуйте что-нибудь сказать для проверки звука")
    print("💡 Совет: Подергайте окно для проверки захвата движения")

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
