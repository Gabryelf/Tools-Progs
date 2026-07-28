"""
Главное окно приложения
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QMessageBox, QFileDialog,
                             QGroupBox, QCheckBox, QComboBox, QSpinBox,
                             QLineEdit, QTabWidget)
from PyQt5.QtCore import Qt, QTimer

# Исправленные импорты - используем абсолютные пути
from core import ScreenRecorder, SettingsManager
from gui.styles import MAIN_STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.recorder = ScreenRecorder(self.settings)

        # Подключаем callback'и
        self.recorder.add_callback('on_start', self.on_recording_started)
        self.recorder.add_callback('on_stop', self.on_recording_stopped)
        self.recorder.add_callback('on_error', self.on_recording_error)
        self.recorder.add_callback('on_progress', self.on_recording_progress)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('🎥 Screen Recorder')
        self.setGeometry(100, 100, 400, 500)
        self.setMinimumSize(350, 400)
        self.setStyleSheet(MAIN_STYLE)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Заголовок
        title = QLabel('🎥 Запись экрана')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 20px; font-weight: bold; color: #2c3e50;')
        layout.addWidget(title)

        # Вкладки
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Вкладка "Запись"
        record_tab = QWidget()
        record_layout = QVBoxLayout()
        record_tab.setLayout(record_layout)

        # Статус
        self.status_label = QLabel('✅ Готов к записи')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName('statusLabel')
        record_layout.addWidget(self.status_label)

        # Информация о записи
        self.info_label = QLabel('⏱ 00:00:00 | 📹 0 кадров')
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet('color: #666; font-size: 12px;')
        record_layout.addWidget(self.info_label)

        # Кнопки
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton('▶ Начать запись')
        self.start_btn.clicked.connect(self.start_recording)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton('⏹ Остановить')
        self.stop_btn.setObjectName('stopBtn')
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)

        record_layout.addLayout(btn_layout)

        # Настройки быстрого доступа
        settings_group = QGroupBox("⚙️ Быстрые настройки")
        settings_layout = QVBoxLayout()

        # Звук
        audio_layout = QHBoxLayout()
        self.audio_check = QCheckBox("Запись звука")
        self.audio_check.setChecked(self.settings.get('record_audio'))
        self.audio_check.toggled.connect(self.toggle_audio)
        audio_layout.addWidget(self.audio_check)

        settings_layout.addLayout(audio_layout)

        settings_group.setLayout(settings_layout)
        record_layout.addWidget(settings_group)

        tabs.addTab(record_tab, "🎬 Запись")

        # Вкладка "Настройки"
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        settings_tab.setLayout(settings_layout)

        # Папка сохранения
        folder_group = QGroupBox("📁 Папка сохранения")
        folder_layout = QVBoxLayout()

        folder_path_layout = QHBoxLayout()
        self.folder_path = QLineEdit()
        self.folder_path.setText(self.settings.get('save_path'))
        self.folder_path.textChanged.connect(self.on_folder_changed)
        folder_path_layout.addWidget(self.folder_path)

        self.folder_btn = QPushButton("📂 Обзор")
        self.folder_btn.clicked.connect(self.choose_folder)
        folder_path_layout.addWidget(self.folder_btn)

        folder_layout.addLayout(folder_path_layout)
        folder_group.setLayout(folder_layout)
        settings_layout.addWidget(folder_group)

        # Качество видео
        quality_group = QGroupBox("🎬 Качество видео")
        quality_layout = QVBoxLayout()

        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(10, 60)
        self.fps_spin.setValue(self.settings.get('video_fps'))
        self.fps_spin.valueChanged.connect(self.on_fps_changed)
        fps_layout.addWidget(self.fps_spin)
        fps_layout.addStretch()
        quality_layout.addLayout(fps_layout)

        quality_group.setLayout(quality_layout)
        settings_layout.addWidget(quality_group)

        # Звук
        audio_settings_group = QGroupBox("🎵 Настройки звука")
        audio_settings_layout = QVBoxLayout()

        # Частота дискретизации
        sample_layout = QHBoxLayout()
        sample_layout.addWidget(QLabel("Частота (кГц):"))
        self.sample_combo = QComboBox()
        self.sample_combo.addItems(["22.05", "44.1", "48"])
        current_rate = self.settings.get('audio_sample_rate')
        if current_rate == 22050:
            self.sample_combo.setCurrentIndex(0)
        elif current_rate == 48000:
            self.sample_combo.setCurrentIndex(2)
        else:
            self.sample_combo.setCurrentIndex(1)
        self.sample_combo.currentTextChanged.connect(self.on_sample_rate_changed)
        sample_layout.addWidget(self.sample_combo)
        sample_layout.addStretch()
        audio_settings_layout.addLayout(sample_layout)

        audio_settings_group.setLayout(audio_settings_layout)
        settings_layout.addWidget(audio_settings_group)

        # Кнопка сохранения настроек
        save_btn = QPushButton("💾 Сохранить настройки")
        save_btn.clicked.connect(self.save_settings)
        settings_layout.addWidget(save_btn)

        settings_layout.addStretch()
        tabs.addTab(settings_tab, "⚙️ Настройки")

        # Вкладка "О программе"
        about_tab = QWidget()
        about_layout = QVBoxLayout()
        about_tab.setLayout(about_layout)

        about_text = QLabel("""
        <h2>🎥 Screen Recorder</h2>
        <p><b>Версия:</b> 0.0.2</p>
        <p><b>Автор:</b> Gabryelf</p>
        <p>Запись экрана с системным звуком</p>
        <p>Используемые технологии:</p>
        <ul>
            <li>Python 3.10+</li>
            <li>PyQt5</li>
            <li>OpenCV</li>
            <li>FFmpeg</li>
        </ul>
        """)
        about_text.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(about_text)
        about_layout.addStretch()

        tabs.addTab(about_tab, "ℹ️ О программе")

        # Таймер обновления статуса
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)

        self.recording_time = 0

    def start_recording(self):
        if self.recorder.is_recording:
            return

        self.recording_time = 0
        self.recorder.start()

    def stop_recording(self):
        if not self.recorder.is_recording:
            return

        self.stop_btn.setEnabled(False)
        self.status_label.setText('⏳ СОХРАНЕНИЕ...')
        self.status_label.setStyleSheet('background-color: #ffaa00; color: white;')

        self.recorder.stop()

    def on_recording_started(self):
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText('⏺ ИДЕТ ЗАПИСЬ...')
        self.status_label.setStyleSheet('background-color: #ff4444; color: white;')

    def on_recording_stopped(self):
        try:
            output_path = self.recorder.save()
            QMessageBox.information(self, '✅ Готово',
                f'Запись сохранена:\n{output_path}')
        except Exception as e:
            QMessageBox.critical(self, '❌ Ошибка',
                f'Не удалось сохранить запись:\n{str(e)}')

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText('✅ Готов к записи')
        self.status_label.setStyleSheet('background-color: white; color: #333;')
        self.info_label.setText('⏱ 00:00:00 | 📹 0 кадров')

    def on_recording_error(self, error):
        QMessageBox.critical(self, '❌ Ошибка', f'Ошибка записи:\n{error}')
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText('❌ Ошибка')

    def on_recording_progress(self, data):
        duration = data['duration']
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.info_label.setText(f'⏱ {time_str} | 📹 {data["frames"]} кадров')

    def update_status(self):
        if self.recorder.is_recording:
            self.status_label.setText('⏺ ИДЕТ ЗАПИСЬ...')

    def toggle_audio(self, checked):
        self.settings.set('record_audio', checked)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения")
        if folder:
            self.folder_path.setText(folder)
            self.settings.set('save_path', folder)

    def on_folder_changed(self, text):
        self.settings.set('save_path', text)

    def on_fps_changed(self, value):
        self.settings.set('video_fps', value)

    def on_sample_rate_changed(self, text):
        rate = float(text) * 1000
        self.settings.set('audio_sample_rate', int(rate))

    def save_settings(self):
        self.settings.save()
        QMessageBox.information(self, '✅ Готово', 'Настройки сохранены!')

    def closeEvent(self, event):
        if self.recorder.is_recording:
            reply = QMessageBox.question(self, 'Подтверждение',
                                         'Запись еще идет. Остановить и выйти?',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.recorder.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()