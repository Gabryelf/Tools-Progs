"""
Модуль записи с поддержкой оверлея для рисования
"""

import threading
import time
from datetime import datetime
import os
import tempfile
import shutil

import cv2
import numpy as np
import sounddevice as sd
import soundfile as sf
import pyautogui

try:
    from moviepy.editor import VideoFileClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from .settings import SettingsManager


class RecorderWithOverlay:
    """Класс для записи экрана с поддержкой оверлея"""

    def __init__(self, settings: SettingsManager = None):
        self.settings = settings or SettingsManager()
        self.is_recording = False
        self.video_writer = None
        self.audio_data = []
        self.temp_dir = tempfile.mkdtemp()
        self.temp_files = None
        self.thread = None
        self.overlay_widget = None
        self.callbacks = {
            'on_start': [],
            'on_stop': [],
            'on_error': [],
            'on_progress': []
        }

    def set_overlay_widget(self, overlay_widget):
        """Установить виджет оверлея"""
        self.overlay_widget = overlay_widget
        if overlay_widget:
            print("✅ Оверлей установлен в рекордер")
        else:
            print("❌ Оверлей удален из рекордера")

    def add_callback(self, event: str, callback):
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def start(self):
        if self.is_recording:
            return

        self.is_recording = True
        self.audio_data = []

        self.thread = threading.Thread(target=self._record)
        self.thread.daemon = True
        self.thread.start()

        self._emit('on_start')

    def stop(self):
        if not self.is_recording:
            return

        self.is_recording = False
        if self.thread:
            self.thread.join(timeout=5)

        self._emit('on_stop')
        return self.temp_files

    def _capture_overlay(self):
        """Захватить оверлей"""
        if self.overlay_widget and self.overlay_widget.isVisible():
            try:
                overlay_pixmap = self.overlay_widget.get_image()
                if overlay_pixmap and not overlay_pixmap.isNull():
                    qimage = overlay_pixmap.toImage()
                    qimage = qimage.convertToFormat(4)
                    width = qimage.width()
                    height = qimage.height()

                    if width > 0 and height > 0:
                        ptr = qimage.bits()
                        ptr.setsize(qimage.byteCount())
                        overlay_array = np.array(ptr).reshape(height, width, 4)
                        return overlay_array
            except Exception as e:
                print(f"⚠️ Ошибка захвата оверлея: {e}")
        return None

    def _apply_overlay(self, frame, overlay_array):
        """Наложить оверлей на кадр"""
        if overlay_array is None:
            return frame

        try:
            h, w = overlay_array.shape[:2]
            frame_h, frame_w = frame.shape[:2]

            # Масштабируем если нужно
            if h != frame_h or w != frame_w:
                overlay_array = cv2.resize(overlay_array, (frame_w, frame_h))
                h, w = overlay_array.shape[:2]

            # Альфа-канал для прозрачности
            alpha = overlay_array[:, :, 3].astype(np.float32) / 255.0
            overlay_rgb = overlay_array[:, :, :3].astype(np.float32)

            # Проверяем есть ли что рисовать
            if np.max(alpha) > 0:
                # Наложение
                for c in range(3):
                    frame[:, :, c] = (
                        frame[:, :, c] * (1 - alpha) +
                        overlay_rgb[:, :, c] * alpha
                    ).astype(np.uint8)

        except Exception as e:
            print(f"⚠️ Ошибка наложения: {e}")

        return frame

    def _record(self):
        try:
            screen_width, screen_height = pyautogui.size()
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            timestamp = datetime.now().strftime("%Y-%d-%m_%H-%M-%S")

            temp_video_file = os.path.join(self.temp_dir, f'temp_video_{timestamp}.mp4')
            self.video_writer = cv2.VideoWriter(
                temp_video_file, fourcc,
                self.settings.get('video_fps'),
                (screen_width, screen_height)
            )

            audio_stream = None
            if self.settings.get('record_audio'):
                audio_stream = self._setup_audio()

            frame_count = 0
            start_time = time.time()

            print(f"🎬 Запись начата: {screen_width}x{screen_height}")

            while self.is_recording:
                try:
                    # Захват экрана
                    screenshot = pyautogui.screenshot()
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    # Захват и наложение оверлея
                    if self.overlay_widget and self.overlay_widget.isVisible():
                        overlay = self._capture_overlay()
                        if overlay is not None:
                            frame = self._apply_overlay(frame, overlay)
                            if frame_count % 30 == 0:  # Каждые 30 кадров
                                print(f"🖍️ Оверлей применен к кадру {frame_count}")

                    self.video_writer.write(frame)
                    frame_count += 1

                    if frame_count % 30 == 0:
                        duration = time.time() - start_time
                        fps = frame_count / duration
                        self._emit('on_progress', {
                            'frames': frame_count,
                            'fps': fps,
                            'duration': duration
                        })

                except Exception as e:
                    self._emit('on_error', f"Ошибка записи: {str(e)}")
                    break

            if audio_stream:
                audio_stream.stop()
                audio_stream.close()

            if self.video_writer:
                self.video_writer.release()

            self._save_audio(timestamp, temp_video_file)
            print("⏹ Запись остановлена")

        except Exception as e:
            self._emit('on_error', str(e))
            self.is_recording = False

    def _setup_audio(self):
        """Настройка аудио"""
        device = self.settings.get('audio_device')

        if device is None:
            try:
                devices = sd.query_devices()
                for i, dev in enumerate(devices):
                    if dev['max_input_channels'] > 0:
                        if 'loopback' in dev['name'].lower():
                            device = i
                            break
            except:
                pass

        if device is None:
            try:
                device = sd.default.device[0]
            except:
                device = None

        stream = sd.InputStream(
            samplerate=self.settings.get('audio_sample_rate'),
            channels=self.settings.get('audio_channels'),
            device=device,
            callback=self._audio_callback
        )
        stream.start()
        return stream

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(f"🎵 Аудио статус: {status}")
        if self.is_recording:
            self.audio_data.append(indata.copy())

    def _save_audio(self, timestamp: str, video_path: str):
        if self.audio_data and self.settings.get('record_audio'):
            temp_audio_file = os.path.join(self.temp_dir, f'temp_audio_{timestamp}.wav')
            audio_array = np.concatenate(self.audio_data, axis=0)
            sf.write(temp_audio_file, audio_array, self.settings.get('audio_sample_rate'))
            self.temp_files = (video_path, temp_audio_file)
        else:
            self.temp_files = (video_path, None)

    def save(self, output_path: str = None):
        if not self.temp_files:
            raise Exception("Нет данных для сохранения")

        video_path, audio_path = self.temp_files

        if output_path is None:
            timestamp = datetime.now().strftime("%Y-%d-%m_%H-%M-%S")
            template = self.settings.get('filename_template')
            filename = template.format(timestamp=timestamp)
            save_dir = self.settings.get('save_path')
            output_path = os.path.join(save_dir, f"{filename}.mp4")

        print(f"\n💾 Сохранение в: {output_path}")

        if (audio_path and os.path.exists(audio_path) and
                self.settings.get('record_audio') and MOVIEPY_AVAILABLE):
            try:
                print("🔄 Объединение видео и аудио...")
                video = VideoFileClip(video_path)
                audio = AudioFileClip(audio_path)

                if audio.duration > video.duration:
                    audio = audio.subclip(0, video.duration)

                final = video.set_audio(audio)
                final.write_videofile(output_path, codec='libx264',
                                      audio_codec='aac',
                                      fps=self.settings.get('video_fps'),
                                      verbose=False, logger=None)

                video.close()
                audio.close()
                final.close()

                try:
                    os.remove(video_path)
                    os.remove(audio_path)
                except:
                    pass

                print(f"✅ Запись сохранена успешно!")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                shutil.copy2(video_path, output_path)
        else:
            print("💾 Сохраняю видео без звука...")
            shutil.copy2(video_path, output_path)

        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

        return output_path

    def _emit(self, event: str, data=None):
        for callback in self.callbacks.get(event, []):
            try:
                if data:
                    callback(data)
                else:
                    callback()
            except Exception as e:
                print(f"⚠️ Ошибка в callback {event}: {e}")
