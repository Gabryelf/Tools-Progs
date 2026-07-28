"""
Screen Recorder - запись экрана и системного звука
"""

import sys
import threading
import time
from datetime import datetime
import os
import tempfile
import shutil

try:
    import cv2
    import numpy as np
    import sounddevice as sd
    import soundfile as sf
    import pyautogui
    from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                                 QVBoxLayout, QLabel, QMessageBox)
    from PyQt5.QtCore import Qt, QTimer
    from moviepy.editor import VideoFileClip, AudioFileClip
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("\nУстановите зависимости командой:")
    print("pip install sounddevice soundfile opencv-python pyautogui numpy PyQt5 moviepy")
    input("\nНажмите Enter для выхода...")
    sys.exit(1)


class ScreenRecorderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_recording = False
        self.recording_thread = None
        self.video_writer = None
        self.audio_data = []
        self.fs = 44100
        self.temp_dir = tempfile.mkdtemp()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.temp_files = None

    def initUI(self):
        self.setWindowTitle('🎥 Screen Recorder')
        self.setGeometry(100, 100, 350, 220)
        self.setFixedSize(350, 220)

        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5f5f5, stop:1 #e8e8e8);
                font-family: 'Segoe UI', Arial;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
            QPushButton#stopBtn {
                background-color: #f44336;
            }
            QPushButton#stopBtn:hover {
                background-color: #da190b;
            }
            QPushButton#stopBtn:disabled {
                background-color: #cccccc;
                color: #888888;
            }
            QLabel {
                font-size: 13px;
                color: #333333;
            }
            QLabel#statusLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
                border-radius: 4px;
                background-color: white;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        title = QLabel('🎥 Запись экрана')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #2c3e50;')
        layout.addWidget(title)

        self.status_label = QLabel('✅ Готов к записи')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName('statusLabel')
        layout.addWidget(self.status_label)

        self.start_btn = QPushButton('▶ Начать запись')
        self.start_btn.clicked.connect(self.start_recording)
        layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton('⏹ Остановить запись')
        self.stop_btn.setObjectName('stopBtn')
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)

        self.info_label = QLabel('📹 Запись экрана + системный звук')
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet('color: #666; font-size: 11px;')
        layout.addWidget(self.info_label)

        self.setLayout(layout)

    def start_recording(self):
        if self.is_recording:
            return

        self.is_recording = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText('⏺ ИДЕТ ЗАПИСЬ...')
        self.status_label.setStyleSheet('background-color: #ff4444; color: white;')
        self.audio_data = []

        self.recording_thread = threading.Thread(target=self.record_screen_and_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        self.timer.start(100)

    def stop_recording(self):
        if not self.is_recording:
            return

        self.is_recording = False
        self.stop_btn.setEnabled(False)
        self.status_label.setText('⏳ СОХРАНЕНИЕ...')
        self.status_label.setStyleSheet('background-color: #ffaa00; color: white;')

        self.timer.stop()
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=5)

        try:
            self.save_video_with_audio()
            QMessageBox.information(self, '✅ Готово',
                                    'Запись успешно сохранена на рабочий стол!')
        except Exception as e:
            QMessageBox.critical(self, '❌ Ошибка',
                                 f'Не удалось сохранить запись:\n{str(e)}')

        self.start_btn.setEnabled(True)
        self.status_label.setText('✅ Готов к записи')
        self.status_label.setStyleSheet('background-color: white; color: #333;')

    def record_screen_and_audio(self):
        try:
            screen_width, screen_height = pyautogui.size()
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            temp_video_file = os.path.join(self.temp_dir, f'temp_video_{timestamp}.mp4')

            self.video_writer = cv2.VideoWriter(temp_video_file, fourcc, 20.0,
                                                (screen_width, screen_height))

            # Поиск устройства для записи звука
            device_info = None
            try:
                devices = sd.query_devices()
                print("\n🎵 Доступные аудиоустройства:")
                for i, dev in enumerate(devices):
                    if dev['max_input_channels'] > 0:
                        print(f"  [{i}] {dev['name']}")
                        if 'loopback' in dev['name'].lower() or 'stereo mix' in dev['name'].lower():
                            device_info = i
                            print(f"  ✅ НАЙДЕНО: {dev['name']}")
            except Exception as e:
                print(f"⚠️ Ошибка поиска устройств: {e}")

            # Если loopback не найден, используем устройство по умолчанию
            if device_info is None:
                try:
                    device_info = sd.default.device[0]
                    print(f"ℹ️ Использую устройство по умолчанию")
                except:
                    device_info = None
                    print("⚠️ Устройство по умолчанию не найдено")

            # Запуск аудио потока
            audio_stream = sd.InputStream(
                samplerate=self.fs,
                channels=2,
                device=device_info,
                callback=self.audio_callback
            )
            audio_stream.start()

            # Запись видео
            frame_count = 0
            start_time = time.time()
            last_time = start_time

            print(f"\n🎬 Начало записи: {screen_width}x{screen_height}")

            while self.is_recording:
                try:
                    screenshot = pyautogui.screenshot()
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    self.video_writer.write(frame)

                    frame_count += 1

                    if time.time() - last_time >= 1.0:
                        fps = frame_count / (time.time() - start_time)
                        print(f"⏺ Кадров: {frame_count}, FPS: {fps:.1f}", end='\r')
                        last_time = time.time()

                except Exception as e:
                    print(f"\n❌ Ошибка записи: {e}")
                    break

            print("\n⏹ Остановка записи...")

            # Освобождение ресурсов
            audio_stream.stop()
            audio_stream.close()
            if self.video_writer:
                self.video_writer.release()

            # Сохранение аудио
            if self.audio_data:
                temp_audio_file = os.path.join(self.temp_dir, f'temp_audio_{timestamp}.wav')
                audio_array = np.concatenate(self.audio_data, axis=0)
                sf.write(temp_audio_file, audio_array, self.fs)
                self.temp_files = (temp_video_file, temp_audio_file)
            else:
                self.temp_files = (temp_video_file, None)
                print("⚠️ Аудио не записано")

        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            self.is_recording = False

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"🎵 Аудио статус: {status}")
        if self.is_recording:
            self.audio_data.append(indata.copy())

    def save_video_with_audio(self):
        if not self.temp_files:
            raise Exception("Нет данных для сохранения")

        temp_video_path, temp_audio_path = self.temp_files
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f'Запись_экрана_{timestamp}.mp4'

        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        output_path = os.path.join(desktop, output_filename)

        print(f"\n💾 Сохранение в: {output_path}")

        if temp_audio_path and os.path.exists(temp_audio_path) and len(self.audio_data) > 0:
            print("🔄 Объединение видео и аудио...")

            try:
                video_clip = VideoFileClip(temp_video_path)
                audio_clip = AudioFileClip(temp_audio_path)

                print(f"📹 Видео: {video_clip.duration:.1f} сек")
                print(f"🎵 Аудио: {audio_clip.duration:.1f} сек")

                if audio_clip.duration > video_clip.duration:
                    audio_clip = audio_clip.subclip(0, video_clip.duration)
                    print(f"✂️ Аудио обрезано до {video_clip.duration:.1f} сек")

                final_clip = video_clip.set_audio(audio_clip)
                final_clip.write_videofile(output_path,
                                           codec='libx264',
                                           audio_codec='aac',
                                           fps=20,
                                           verbose=False,
                                           logger=None)

                video_clip.close()
                audio_clip.close()
                final_clip.close()

                print(f"✅ Запись сохранена!")

            except Exception as e:
                print(f"❌ Ошибка при объединении: {e}")
                os.rename(temp_video_path, output_path)
                print(f"✅ Сохранено видео без звука")
        else:
            os.rename(temp_video_path, output_path)
            print(f"✅ Сохранено видео без звука")

        # Очистка
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def update_status(self):
        if self.is_recording:
            self.status_label.setText('⏺ ИДЕТ ЗАПИСЬ...')
        else:
            self.status_label.setText('⏳ СОХРАНЕНИЕ...')

    def closeEvent(self, event):
        if self.is_recording:
            reply = QMessageBox.question(self, 'Подтверждение',
                                         'Запись еще идет. Остановить и выйти?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.stop_recording()
                event.accept()
            else:
                event.ignore()
        else:
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScreenRecorderApp()
    window.show()
    sys.exit(app.exec_())