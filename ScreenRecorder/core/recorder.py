"""
Модуль записи экрана и звука
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
from .audio_processor import AudioProcessor


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
        self.audio_processor = None
        self.callbacks = {
            'on_start': [],
            'on_stop': [],
            'on_error': [],
            'on_progress': []
        }

    def add_callback(self, event: str, callback):
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def start(self):
        if self.is_recording:
            return

        # Инициализируем обработчик аудио
        if self.settings.get('record_audio'):
            sample_rate = self.settings.get('audio_sample_rate')
            self.audio_processor = AudioProcessor(sample_rate)
            print("🔇 Шумоподавление готово (фильтр высоких частот)")

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

    def _record(self):
        """Основной цикл записи"""
        try:
            screen_width, screen_height = pyautogui.size()
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            timestamp = datetime.now().strftime("%Y-%d-%m_%H-%M-%S")
            temp_video_file = os.path.join(self.temp_dir, f'temp_video_{timestamp}.avi')

            self.video_writer = cv2.VideoWriter(
                temp_video_file, fourcc,
                self.settings.get('video_fps'),
                (screen_width, screen_height)
            )

            if not self.video_writer.isOpened():
                raise Exception("Не удалось создать VideoWriter")

            audio_stream = None
            if self.settings.get('record_audio'):
                audio_stream = self._setup_audio()

            frame_count = 0
            start_time = time.time()
            last_progress_time = start_time

            print(f"🎬 Запись начата: {screen_width}x{screen_height}")

            while self.is_recording:
                try:
                    screenshot = pyautogui.screenshot()
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    self.video_writer.write(frame)
                    frame_count += 1

                    current_time = time.time()
                    if current_time - last_progress_time >= 1.0:
                        duration = current_time - start_time
                        fps = frame_count / duration if duration > 0 else 0
                        self._emit('on_progress', {
                            'frames': frame_count,
                            'fps': fps,
                            'duration': duration
                        })
                        last_progress_time = current_time

                except Exception as e:
                    self._emit('on_error', f"Ошибка записи кадра: {str(e)}")
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

        if device is not None:
            stream = sd.InputStream(
                samplerate=self.settings.get('audio_sample_rate'),
                channels=self.settings.get('audio_channels'),
                device=device,
                callback=self._audio_callback
            )
            stream.start()
            return stream
        return None

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(f"🎵 Аудио статус: {status}")
        if self.is_recording:
            self.audio_data.append(indata.copy())

    def _save_audio(self, timestamp: str, video_path: str):
        """Сохранение аудио с простым фильтром высоких частот"""
        if self.audio_data and self.settings.get('record_audio'):
            try:
                temp_audio_file = os.path.join(self.temp_dir, f'temp_audio_{timestamp}.wav')

                # Объединяем аудио
                audio_array = np.concatenate(self.audio_data, axis=0)

                # Шумоподавление - только фильтр высоких частот
                if self.settings.get('noise_reduction') and self.audio_processor:
                    print("🔇 Применение фильтра высоких частот...")

                    # Применяем фильтр для удаления низкочастотного гула
                    audio_array = self.audio_processor.apply_highpass_filter(
                        audio_array,
                        cutoff_freq=80
                    )

                    print("✅ Фильтр применен")

                # Нормализация
                max_val = np.max(np.abs(audio_array))
                if max_val > 0.01:
                    audio_array = audio_array / max_val * 0.9

                # Сохраняем
                sf.write(temp_audio_file, audio_array, self.settings.get('audio_sample_rate'))
                self.temp_files = (video_path, temp_audio_file)
                print(f"🎵 Аудио сохранено: {len(audio_array)} семплов")

            except Exception as e:
                print(f"⚠️ Ошибка сохранения аудио: {e}")
                self.temp_files = (video_path, None)
        else:
            self.temp_files = (video_path, None)

    def save(self, output_path: str = None):
        """Быстрое сохранение"""
        if not self.temp_files:
            raise Exception("Нет данных для сохранения")

        video_path, audio_path = self.temp_files

        if output_path is None:
            timestamp = datetime.now().strftime("%Y-%d-%m_%H-%M-%S")
            template = self.settings.get('filename_template')
            filename = template.format(timestamp=timestamp)
            save_dir = self.settings.get('save_path')
            output_path = os.path.join(save_dir, f"{filename}.mp4")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"\n💾 Сохранение в: {output_path}")

        has_audio = (audio_path and os.path.exists(audio_path) and
                    self.settings.get('record_audio'))

        if has_audio and MOVIEPY_AVAILABLE:
            try:
                self._save_fast_with_moviepy(video_path, audio_path, output_path)
            except Exception as e:
                print(f"❌ Ошибка сохранения: {e}")
                print("💾 Сохраняю видео без звука...")
                shutil.copy2(video_path, output_path)
                self._cleanup_temp_files(video_path, audio_path)
        else:
            print("💾 Сохраняю видео без звука...")
            shutil.copy2(video_path, output_path)
            self._cleanup_temp_files(video_path, audio_path)

        return output_path

    def _save_fast_with_moviepy(self, video_path, audio_path, output_path):
        """Быстрое сохранение через moviepy"""
        print("🔄 Быстрое объединение видео и аудио...")

        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)

        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)

        final = video.set_audio(audio)

        # Быстрое сохранение
        final.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=self.settings.get('video_fps'),
            preset='ultrafast',
            bitrate='2000k',
            audio_bitrate='128k',
            threads=4,
            verbose=False,
            logger=None
        )

        video.close()
        audio.close()
        final.close()

        self._cleanup_temp_files(video_path, audio_path)
        print(f"✅ Запись сохранена успешно!")

    def _cleanup_temp_files(self, video_path, audio_path=None):
        """Очистка временных файлов"""
        try:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"⚠️ Ошибка очистки временных файлов: {e}")

    def _emit(self, event: str, data=None):
        for callback in self.callbacks.get(event, []):
            try:
                if data:
                    callback(data)
                else:
                    callback()
            except Exception as e:
                print(f"⚠️ Ошибка в callback {event}: {e}")