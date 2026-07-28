"""
Модуль записи экрана и звука
"""

import threading
import time
from datetime import datetime
import os
import tempfile
import shutil
import subprocess

import cv2
import numpy as np
import sounddevice as sd
import soundfile as sf
import pyautogui

# Пробуем импортировать moviepy с обработкой ошибок
try:
    from moviepy.editor import VideoFileClip, AudioFileClip

    MOVIEPY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MoviePy не установлен: {e}")
    print("Для установки выполните: pip install moviepy")
    MOVIEPY_AVAILABLE = False

from .settings import SettingsManager


class ScreenRecorder:
    """Класс для записи экрана и звука"""

    def __init__(self, settings: SettingsManager = None):
        self.settings = settings or SettingsManager()
        self.is_recording = False
        self.video_writer = None
        self.audio_data = []
        self.temp_dir = tempfile.mkdtemp()
        self.temp_files = None
        self.thread = None
        self.callbacks = {
            'on_start': [],
            'on_stop': [],
            'on_error': [],
            'on_progress': []
        }

        # Проверка moviepy
        if not MOVIEPY_AVAILABLE:
            print("⚠️ Видео будет сохраняться без звука (требуется moviepy)")

    def add_callback(self, event: str, callback):
        """Добавить callback на событие"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def start(self):
        """Начать запись"""
        if self.is_recording:
            return

        self.is_recording = True
        self.audio_data = []

        self.thread = threading.Thread(target=self._record)
        self.thread.daemon = True
        self.thread.start()

        self._emit('on_start')

    def stop(self):
        """Остановить запись"""
        if not self.is_recording:
            return

        self.is_recording = False
        if self.thread:
            self.thread.join(timeout=5)

        self._emit('on_stop')
        return self.temp_files

    def _record(self):
        """Основной цикл записи"""
        try:
            screen_width, screen_height = pyautogui.size()
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            temp_video_file = os.path.join(self.temp_dir, f'temp_video_{timestamp}.mp4')
            self.video_writer = cv2.VideoWriter(
                temp_video_file, fourcc,
                self.settings.get('video_fps'),
                (screen_width, screen_height)
            )

            # Настройка аудио
            audio_stream = None
            if self.settings.get('record_audio'):
                audio_stream = self._setup_audio()

            # Запись
            frame_count = 0
            start_time = time.time()
            last_time = start_time

            print(f"🎬 Запись начата: {screen_width}x{screen_height}")

            while self.is_recording:
                try:
                    screenshot = pyautogui.screenshot()
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    self.video_writer.write(frame)

                    frame_count += 1

                    if time.time() - last_time >= 1.0:
                        fps = frame_count / (time.time() - start_time)
                        self._emit('on_progress', {
                            'frames': frame_count,
                            'fps': fps,
                            'duration': time.time() - start_time
                        })
                        last_time = time.time()

                except Exception as e:
                    self._emit('on_error', f"Ошибка записи кадра: {str(e)}")
                    break

            # Освобождение ресурсов
            if audio_stream:
                audio_stream.stop()
                audio_stream.close()

            if self.video_writer:
                self.video_writer.release()

            # Сохранение аудио
            self._save_audio(timestamp, temp_video_file)

            print("⏹ Запись остановлена")

        except Exception as e:
            self._emit('on_error', str(e))
            self.is_recording = False

    def _setup_audio(self):
        """Настройка аудиозаписи"""
        device = self.settings.get('audio_device')

        # Если устройство не указано, ищем loopback
        if device is None:
            try:
                devices = sd.query_devices()
                print("\n🎵 Доступные аудиоустройства:")
                for i, dev in enumerate(devices):
                    if dev['max_input_channels'] > 0:
                        print(f"  [{i}] {dev['name']}")
                        if 'loopback' in dev['name'].lower() or 'stereo mix' in dev['name'].lower():
                            device = i
                            print(f"  ✅ Найдено устройство loopback: {dev['name']}")
                            break
            except Exception as e:
                print(f"⚠️ Ошибка поиска устройств: {e}")

        # Если loopback не найден, используем устройство по умолчанию
        if device is None:
            try:
                device = sd.default.device[0]
                print(f"ℹ️ Использую устройство по умолчанию")
            except:
                device = None
                print("⚠️ Устройство по умолчанию не найдено")

        stream = sd.InputStream(
            samplerate=self.settings.get('audio_sample_rate'),
            channels=self.settings.get('audio_channels'),
            device=device,
            callback=self._audio_callback
        )
        stream.start()
        return stream

    def _audio_callback(self, indata, frames, time, status):
        """Callback для аудио"""
        if status:
            print(f"🎵 Аудио статус: {status}")
        if self.is_recording:
            self.audio_data.append(indata.copy())

    def _save_audio(self, timestamp: str, video_path: str):
        """Сохранение аудио и объединение с видео"""
        if self.audio_data and self.settings.get('record_audio'):
            temp_audio_file = os.path.join(self.temp_dir, f'temp_audio_{timestamp}.wav')
            audio_array = np.concatenate(self.audio_data, axis=0)
            sf.write(temp_audio_file, audio_array, self.settings.get('audio_sample_rate'))
            self.temp_files = (video_path, temp_audio_file)
            print(f"🎵 Аудио сохранено: {len(self.audio_data)} фрагментов")
        else:
            self.temp_files = (video_path, None)
            if not self.audio_data:
                print("⚠️ Аудио не записано")

    def save(self, output_path: str = None):
        """Сохранить запись в файл"""
        if not self.temp_files:
            raise Exception("Нет данных для сохранения")

        video_path, audio_path = self.temp_files

        if output_path is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            template = self.settings.get('filename_template')
            filename = template.format(timestamp=timestamp)
            save_dir = self.settings.get('save_path')
            output_path = os.path.join(save_dir, f"{filename}.mp4")

        print(f"\n💾 Сохранение в: {output_path}")

        # Объединение с аудио
        if (audio_path and os.path.exists(audio_path) and
                self.settings.get('record_audio') and MOVIEPY_AVAILABLE):
            try:
                print("🔄 Объединение видео и аудио...")
                video = VideoFileClip(video_path)
                audio = AudioFileClip(audio_path)

                print(f"📹 Видео: {video.duration:.1f} сек")
                print(f"🎵 Аудио: {audio.duration:.1f} сек")

                if audio.duration > video.duration:
                    audio = audio.subclip(0, video.duration)
                    print(f"✂️ Аудио обрезано до {video.duration:.1f} сек")

                final = video.set_audio(audio)
                final.write_videofile(output_path,
                                      codec='libx264',
                                      audio_codec='aac',
                                      fps=self.settings.get('video_fps'),
                                      verbose=False,
                                      logger=None)

                video.close()
                audio.close()
                final.close()

                # Удаляем временные файлы
                try:
                    os.remove(video_path)
                    os.remove(audio_path)
                except:
                    pass

                print(f"✅ Запись сохранена успешно!")

            except Exception as e:
                print(f"❌ Ошибка при объединении: {e}")
                print("💾 Сохраняю видео без звука...")
                shutil.copy2(video_path, output_path)
        else:
            # Сохраняем только видео
            print("💾 Сохраняю видео без звука...")
            shutil.copy2(video_path, output_path)

        # Очистка временной папки
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

        return output_path

    def _emit(self, event: str, data=None):
        """Вызов callback'ов"""
        for callback in self.callbacks.get(event, []):
            try:
                if data:
                    callback(data)
                else:
                    callback()
            except Exception as e:
                print(f"⚠️ Ошибка в callback {event}: {e}")

    def __del__(self):
        """Очистка при удалении"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass