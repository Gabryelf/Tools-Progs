"""
Главное окно приложения с поддержкой системного трея
"""
import os
import logging
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QFileDialog,
    QGroupBox, QCheckBox, QComboBox, QSpinBox,
    QLineEdit, QTabWidget, QSystemTrayIcon, QMenu,
    QAction, QApplication, QSlider
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen

from core import SettingsManager, ScreenRecorder
from gui.modern_styles import DARK_STYLE
from constants import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.recorder = ScreenRecorder(self.settings)

        # Устанавливаем иконку окна
        from constants import ICON_PATH
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

        # Подключаем callback'и
        self.recorder.add_callback('on_start', self.on_recording_started)
        self.recorder.add_callback('on_stop', self.on_recording_stopped)
        self.recorder.add_callback('on_error', self.on_recording_error)
        self.recorder.add_callback('on_progress', self.on_recording_progress)

        # Настройка системного трея
        self.tray_icon = None
        self.tray_menu = None
        self.is_minimized = False
        self.compact_widget = None
        self.main_layout = None
        self.last_folder = self.settings.get('save_path')

        self.initUI()
        self.create_tray_icon()
        logger.info("Главное окно инициализировано")

    def initUI(self):
        """Инициализация интерфейса"""
        self.setWindowTitle(f'🎥 {APP_NAME}')
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(400, 600)
        self.setStyleSheet(DARK_STYLE)

        # Создаем центральный виджет и основной layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # Создаем компактный режим (минимальный)
        self.compact_widget = self.create_compact_mode()
        self.compact_widget.hide()
        self.main_layout.addWidget(self.compact_widget)

        # Создаем полноценный интерфейс
        self.full_widget = self.create_full_mode()
        self.main_layout.addWidget(self.full_widget)

        # Таймер обновления статуса
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)

    def create_compact_mode(self):
        """Создать компактный режим с кнопками стоп и развернуть"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 8px;
                border: 1px solid #3c3c3c;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton#stopCompactBtn {
                background-color: #d32f2f;
                color: white;
            }
            QPushButton#stopCompactBtn:hover {
                background-color: #e53935;
            }
            QPushButton#expandBtn {
                background-color: #007acc;
                color: white;
            }
            QPushButton#expandBtn:hover {
                background-color: #1a8ad4;
            }
            QLabel {
                color: #d4d4d4;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Статус в компактном режиме
        self.compact_status = QLabel('⏺ ЗАПИСЬ...')
        self.compact_status.setStyleSheet("color: #ff6b6b; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.compact_status)
        layout.addStretch()

        # Время записи
        self.compact_time = QLabel('00:00:00')
        self.compact_time.setStyleSheet("color: #888888; font-size: 14px;")
        layout.addWidget(self.compact_time)
        layout.addStretch()

        # Кнопка остановить
        self.stop_compact_btn = QPushButton('⏹ Остановить')
        self.stop_compact_btn.setObjectName('stopCompactBtn')
        self.stop_compact_btn.clicked.connect(self.stop_recording)
        self.stop_compact_btn.setEnabled(False)
        layout.addWidget(self.stop_compact_btn)

        # Кнопка развернуть
        self.expand_btn = QPushButton('📂 Развернуть')
        self.expand_btn.setObjectName('expandBtn')
        self.expand_btn.clicked.connect(self.expand_window)
        layout.addWidget(self.expand_btn)

        widget.setLayout(layout)
        return widget

    def create_full_mode(self):
        """Создать полноценный интерфейс"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Заголовок
        title = QLabel(f'🎥 {APP_NAME}')
        title.setObjectName('titleLabel')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Вкладки
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # ============ Вкладка "Запись" ============
        record_tab = QWidget()
        record_layout = QVBoxLayout()
        record_tab.setLayout(record_layout)

        # Статус
        self.status_label = QLabel('✅ Готов к записи')
        self.status_label.setObjectName('statusLabel')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setProperty('class', 'ready')
        record_layout.addWidget(self.status_label)

        # Информация о записи
        self.info_label = QLabel('⏱ 00:00:00 | 📹 0 кадров')
        self.info_label.setObjectName('infoLabel')
        self.info_label.setAlignment(Qt.AlignCenter)
        record_layout.addWidget(self.info_label)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton('▶ Начать запись')
        self.start_btn.setObjectName('startBtn')
        self.start_btn.clicked.connect(self.start_recording)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton('⏹ Остановить')
        self.stop_btn.setObjectName('stopBtn')
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        record_layout.addLayout(btn_layout)

        # Кнопка свернуть в трей
        minimize_layout = QHBoxLayout()
        self.minimize_btn = QPushButton('🔽 Свернуть в трей')
        self.minimize_btn.setObjectName('minimizeBtn')
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
        """)
        self.minimize_btn.clicked.connect(self.minimize_to_tray)
        minimize_layout.addWidget(self.minimize_btn)
        minimize_layout.addStretch()
        record_layout.addLayout(minimize_layout)

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
        record_layout.addStretch()

        tabs.addTab(record_tab, "🎬 Запись")

        # ============ Вкладка "Настройки" ============
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        settings_tab.setLayout(settings_layout)

        # ===== ПАПКА СОХРАНЕНИЯ =====
        folder_group = QGroupBox("📁 Папка сохранения")
        folder_layout = QVBoxLayout()

        # Текущая папка
        folder_info_layout = QHBoxLayout()
        folder_info_layout.addWidget(QLabel("Текущая папка:"))
        folder_info_layout.addStretch()
        folder_layout.addLayout(folder_info_layout)

        # Отображение пути с кнопкой открыть
        folder_path_layout = QHBoxLayout()
        self.folder_path = QLineEdit()
        self.folder_path.setText(self.settings.get('save_path'))
        self.folder_path.setReadOnly(True)
        self.folder_path.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 8px 10px;
                font-size: 12px;
            }
            QLineEdit:hover {
                border-color: #007acc;
            }
        """)
        folder_path_layout.addWidget(self.folder_path, 1)

        # Кнопка открыть папку
        self.open_folder_btn = QPushButton("📂 Открыть")
        self.open_folder_btn.setToolTip("Открыть папку в проводнике")
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                padding: 8px 12px;
                border-radius: 4px;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
                border-color: #007acc;
            }
        """)
        self.open_folder_btn.clicked.connect(self.open_save_folder)
        folder_path_layout.addWidget(self.open_folder_btn)
        folder_layout.addLayout(folder_path_layout)

        # Кнопка выбора папки
        select_folder_layout = QHBoxLayout()
        self.select_folder_btn = QPushButton("📁 Выбрать другую папку")
        self.select_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #1a8ad4;
            }
        """)
        self.select_folder_btn.clicked.connect(self.choose_folder)
        select_folder_layout.addWidget(self.select_folder_btn)
        select_folder_layout.addStretch()
        folder_layout.addLayout(select_folder_layout)

        # Кнопка использовать папку по умолчанию
        default_folder_layout = QHBoxLayout()
        self.default_folder_btn = QPushButton("🔄 Использовать папку по умолчанию")
        self.default_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
        """)
        self.default_folder_btn.clicked.connect(self.set_default_folder)
        default_folder_layout.addWidget(self.default_folder_btn)
        default_folder_layout.addStretch()
        folder_layout.addLayout(default_folder_layout)

        folder_group.setLayout(folder_layout)
        settings_layout.addWidget(folder_group)

        # ===== КАЧЕСТВО ВИДЕО =====
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

        # ===== НАСТРОЙКИ ЗВУКА =====
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

        # ===== ШУМОПОДАВЛЕНИЕ =====
        noise_group = QGroupBox("🔇 Шумоподавление")
        noise_layout = QVBoxLayout()

        self.noise_reduction_check = QCheckBox("Включить шумоподавление")
        self.noise_reduction_check.setChecked(self.settings.get('noise_reduction'))
        self.noise_reduction_check.toggled.connect(self.toggle_noise_reduction)
        noise_layout.addWidget(self.noise_reduction_check)

        # Информация
        # info_label = QLabel("💡 Убирает низкочастотный гул (шум кулера, гудение)")
        # info_label.setStyleSheet("color: #888888; font-size: 11px; padding: 5px;")
        # noise_layout.addWidget(info_label)

        # info_label2 = QLabel("✅ Речь и высокие звуки полностью сохраняются")
        # info_label2.setStyleSheet("color: #66bb6a; font-size: 11px; padding: 5px;")
        # noise_layout.addWidget(info_label2)

        # info_label3 = QLabel("ℹ️ Частота среза: 80 Гц")
        # info_label3.setStyleSheet("color: #888888; font-size: 11px; padding: 5px;")
        # noise_layout.addWidget(info_label3)

        noise_group.setLayout(noise_layout)
        audio_settings_layout.addWidget(noise_group)

        audio_settings_group.setLayout(audio_settings_layout)
        settings_layout.addWidget(audio_settings_group)

        # Кнопка сохранения настроек
        save_btn = QPushButton("💾 Сохранить настройки")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        settings_layout.addWidget(save_btn)
        settings_layout.addStretch()

        tabs.addTab(settings_tab, "⚙️ Настройки")

        # ============ Вкладка "О программе" ============
        about_tab = QWidget()
        about_layout = QVBoxLayout()
        about_tab.setLayout(about_layout)
        about_text = QLabel(f"""
        <h2>🎥 {APP_NAME}</h2>
        <p><b>Версия:</b> {APP_VERSION}</p>
        <p><b>Автор:</b> Gabryelf</p>
        <p>Запись экрана с системным звуком</p>
        <p>История версий и возможности приложения:</p>
        <ul>
            <li>v0.0.1 Основной интерфейс и сохранение записи</li>
            <li>v0.0.2 Настройки приложения и запись звука</li>
            <li>v0.0.3 Функция минимизации интерфейса и скрытия в трей</li>
            <li>v0.0.4 Возможность шумоподавления записи звука</li>
        </ul>
        <p>Git Hub: </p>
        <p>https://github.com/Gabryelf/Tools-Progs/tree/main/ScreenRecorder</p>
        """)
        about_text.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(about_text)
        about_layout.addStretch()
        tabs.addTab(about_tab, "ℹ️ О программе")

        return widget

    def create_tray_icon(self):
        """Создание иконки в системном трее"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.create_icon())

        # Создаем меню трея
        self.tray_menu = QMenu()

        # Действия в трее
        self.tray_show_action = QAction("📂 Показать окно", self)
        self.tray_show_action.triggered.connect(self.show_window)
        self.tray_menu.addAction(self.tray_show_action)

        self.tray_menu.addSeparator()

        self.tray_stop_action = QAction("⏹ Остановить запись", self)
        self.tray_stop_action.triggered.connect(self.stop_recording)
        self.tray_stop_action.setEnabled(False)
        self.tray_menu.addAction(self.tray_stop_action)

        self.tray_menu.addSeparator()

        self.tray_quit_action = QAction("❌ Выход", self)
        self.tray_quit_action.triggered.connect(self.quit_application)
        self.tray_menu.addAction(self.tray_quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def create_icon(self):
        """Создать иконку для трея"""
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рисуем круг
        painter.setBrush(QColor(30, 30, 30))
        painter.setPen(QPen(QColor(60, 60, 60), 2))
        painter.drawEllipse(2, 2, size - 4, size - 4)

        # Рисуем иконку камеры
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.drawRect(12, 20, 40, 28)
        painter.drawEllipse(32, 30, 10, 10)  # Объектив

        # Кнопка записи
        painter.setBrush(QColor(200, 50, 50))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(50, 8, 10, 10)
        painter.end()

        return QIcon(pixmap)

    def minimize_to_tray(self):
        """Свернуть в трей"""
        self.is_minimized = True
        self.full_widget.hide()
        self.compact_widget.show()

        # Обновляем размер окна
        self.setFixedHeight(80)
        self.setFixedWidth(400)

        # Показываем уведомление
        self.tray_icon.showMessage(
            APP_NAME,
            "Приложение свернуто в трей. Запись продолжается.",
            QSystemTrayIcon.Information,
            2000
        )

    def expand_window(self):
        """Развернуть окно"""
        self.is_minimized = False
        self.compact_widget.hide()
        self.full_widget.show()

        # Возвращаем нормальный размер
        self.setFixedHeight(WINDOW_HEIGHT)
        self.setFixedWidth(WINDOW_WIDTH)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.show()
        self.activateWindow()

    def show_window(self):
        """Показать окно из трея"""
        if self.is_minimized:
            self.expand_window()
        else:
            self.show()
            self.activateWindow()

    def on_tray_activated(self, reason):
        """Обработка клика по иконке в трее"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()

    def quit_application(self):
        """Выход из приложения"""
        if self.recorder.is_recording:
            reply = QMessageBox.question(
                self, 'Подтверждение',
                'Запись еще идет. Остановить и выйти?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.recorder.stop()
                QApplication.quit()
            else:
                return
        else:
            QApplication.quit()

    def start_recording(self):
        """Начать запись"""
        if self.recorder.is_recording:
            return
        self.recorder.start()

    def stop_recording(self):
        """Остановить запись"""
        if not self.recorder.is_recording:
            return

        # Отключаем кнопки
        self.stop_btn.setEnabled(False)
        self.stop_compact_btn.setEnabled(False)
        self.tray_stop_action.setEnabled(False)

        self.status_label.setText('⏳ СОХРАНЕНИЕ...')
        self.status_label.setProperty('class', 'saving')
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

        self.compact_status.setText('⏳ СОХРАНЕНИЕ...')
        self.compact_status.setStyleSheet("color: #ffd93d; font-size: 14px; font-weight: bold;")

        self.recorder.stop()

    def on_recording_started(self):
        """Обработка начала записи"""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.stop_compact_btn.setEnabled(True)
        self.tray_stop_action.setEnabled(True)

        self.status_label.setText('⏺ ИДЕТ ЗАПИСЬ...')
        self.status_label.setProperty('class', 'recording')
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

        self.compact_status.setText('⏺ ЗАПИСЬ...')
        self.compact_status.setStyleSheet("color: #ff6b6b; font-size: 14px; font-weight: bold;")

    def on_recording_stopped(self):
        """Обработка остановки записи"""
        try:
            output_path = self.recorder.save()
            # Показываем уведомление в трее
            self.tray_icon.showMessage(
                "✅ Запись сохранена",
                f"Файл сохранен:\n{os.path.basename(output_path)}",
                QSystemTrayIcon.Information,
                3000
            )
            QMessageBox.information(self, '✅ Готово',
                f'Запись сохранена:\n{output_path}')
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
            QMessageBox.critical(self, '❌ Ошибка',
                f'Не удалось сохранить запись:\n{str(e)}')

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.stop_compact_btn.setEnabled(False)
        self.tray_stop_action.setEnabled(False)

        self.status_label.setText('✅ Готов к записи')
        self.status_label.setProperty('class', 'ready')
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

        self.compact_status.setText('✅ Готов')
        self.compact_status.setStyleSheet("color: #66bb6a; font-size: 14px; font-weight: bold;")

        self.info_label.setText('⏱ 00:00:00 | 📹 0 кадров')
        self.compact_time.setText('00:00:00')

    def on_recording_error(self, error):
        """Обработка ошибки записи"""
        logger.error(f"Ошибка записи: {error}")
        QMessageBox.critical(self, '❌ Ошибка', f'Ошибка записи:\n{error}')
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.stop_compact_btn.setEnabled(False)
        self.tray_stop_action.setEnabled(False)
        self.status_label.setText('❌ Ошибка')
        self.compact_status.setText('❌ Ошибка')

    def on_recording_progress(self, data):
        """Обработка прогресса записи"""
        duration = data['duration']
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.info_label.setText(f'⏱ {time_str} | 📹 {data["frames"]} кадров')
        self.compact_time.setText(time_str)

    def update_status(self):
        """Обновление статуса"""
        if self.recorder.is_recording:
            self.status_label.setText('⏺ ИДЕТ ЗАПИСЬ...')
            self.compact_status.setText('⏺ ЗАПИСЬ...')

    def toggle_audio(self, checked):
        """Включение/выключение записи звука"""
        self.settings.set('record_audio', checked)
        logger.info(f"Запись звука: {'включена' if checked else 'выключена'}")

    def toggle_noise_reduction(self, checked):
        """Включение/выключение шумоподавления"""
        self.settings.set('noise_reduction', checked)
        logger.info(f"Шумоподавление: {'включено' if checked else 'выключено'}")

    def choose_folder(self):
        """Выбор папки через диалог"""
        start_folder = self.last_folder if self.last_folder else self.settings.get('save_path')
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения записей",
            start_folder,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.last_folder = folder
            self.folder_path.setText(folder)
            self.settings.set('save_path', folder)
            logger.info(f"Папка сохранения изменена: {folder}")
            self.tray_icon.showMessage(
                "📁 Папка изменена",
                f"Записи будут сохраняться в:\n{folder}",
                QSystemTrayIcon.Information,
                2000
            )

    def open_save_folder(self):
        """Открыть папку сохранения в проводнике"""
        folder = self.settings.get('save_path')
        if os.path.exists(folder):
            os.startfile(folder)
        else:
            QMessageBox.warning(self, 'Ошибка', f'Папка не существует:\n{folder}')

    def set_default_folder(self):
        """Установить папку по умолчанию (Рабочий стол)"""
        default_folder = os.path.join(os.path.expanduser("~"), "Desktop")
        self.folder_path.setText(default_folder)
        self.settings.set('save_path', default_folder)
        self.last_folder = default_folder
        logger.info(f"Папка сохранения сброшена на: {default_folder}")
        QMessageBox.information(self, '✅ Готово',
            f'Папка сохранения изменена на:\n{default_folder}')

    def on_fps_changed(self, value):
        """Изменение FPS"""
        self.settings.set('video_fps', value)
        logger.info(f"FPS изменен: {value}")

    def on_sample_rate_changed(self, text):
        """Изменение частоты дискретизации"""
        rate = float(text) * 1000
        self.settings.set('audio_sample_rate', int(rate))
        logger.info(f"Частота дискретизации изменена: {rate}")

    def save_settings(self):
        """Сохранение настроек"""
        self.settings.save()
        QMessageBox.information(self, '✅ Готово', 'Настройки сохранены!')

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.recorder.is_recording:
            if not self.is_minimized:
                self.minimize_to_tray()
                event.ignore()
                return

        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите выйти?',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.recorder.is_recording:
                self.recorder.stop()
            logger.info("Приложение закрыто")
            event.accept()
        else:
            event.ignore()
