"""
Модуль записи экрана и звука
"""
import threading
import time
import logging
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Callable, Tuple, Any

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

logger = logging.getLogger(__name__)


class RecorderEvents:
    """Типы событий для колбэков"""
    ON_START = 'on_start'
    ON_STOP = 'on_stop'
    ON_ERROR = 'on_error'
    ON_PROGRESS = 'on_progress'


class ScreenRecorder:
    """
    Класс для записи экрана и звука

    Attributes:
        settings: Менеджер настроек
        is_recording: Флаг состояния записи
        callbacks: Словарь с колбэками
    """

    def __init__(self, settings: Optional[SettingsManager] = None):
        self.settings = settings or SettingsManager()
        self._is_recording = False
        self._video_writer: Optional[cv2.VideoWriter] = None
        self._audio_data: List[np.ndarray] = []
        self._temp_dir = tempfile.mkdtemp()
        self._temp_files: Optional[Tuple[str, Optional[str]]] = None
        self._thread: Optional[threading.Thread] = None
        self._audio_stream: Optional[sd.InputStream] = None
        self._audio_processor: Optional[AudioProcessor] = None
        self._callbacks: Dict[str, List[Callable]] = {
            RecorderEvents.ON_START: [],
            RecorderEvents.ON_STOP: [],
            RecorderEvents.ON_ERROR: [],
            RecorderEvents.ON_PROGRESS: []
        }

    @property
    def is_recording(self) -> bool:
        """Проверка состояния записи"""
        return self._is_recording

    @property
    def temp_files(self) -> Optional[Tuple[str, Optional[str]]]:
        """Получение временных файлов"""
        return self._temp_files

    def add_callback(self, event: str, callback: Callable) -> None:
        """
        Добавление колбэка

        Args:
            event: Тип события
            callback: Функция обратного вызова
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def start(self) -> None:
        """Начало записи"""
        if self._is_recording:
            return

        # Инициализация аудио процессора
        if self.settings.get('record_audio'):
            sample_rate = self.settings.get('audio_sample_rate')
            self._audio_processor = AudioProcessor(sample_rate)
            logger.info("Аудио процессор инициализирован")

        self._is_recording = True
        self._audio_data = []

        self._thread = threading.Thread(target=self._record_loop)
        self._thread.daemon = True
        self._thread.start()

        self._emit(RecorderEvents.ON_START)
        logger.info("Запись начата")

    def stop(self) -> Optional[Tuple[str, Optional[str]]]:
        """Остановка записи"""
        if not self._is_recording:
            return None

        self._is_recording = False
        if self._thread:
            self._thread.join(timeout=5)

        self._emit(RecorderEvents.ON_STOP)
        logger.info("Запись остановлена")
        return self._temp_files

    def _record_loop(self) -> None:
        """Основной цикл записи"""
        try:
            screen_width, screen_height = pyautogui.size()
            timestamp = datetime.now().strftime("%Y-%d-%m_%H-%M-%S")

            # Создание временного видеофайла
            temp_video_file = os.path.join(self._temp_dir, f'temp_video_{timestamp}.avi')
            self._video_writer = self._create_video_writer(
                temp_video_file, screen_width, screen_height
            )

            # Настройка аудио
            if self.settings.get('record_audio'):
                self._audio_stream = self._setup_audio_stream()

            frame_count = 0
            start_time = time.time()
            last_progress_time = start_time

            logger.info(f"Запись экрана: {screen_width}x{screen_height}")

            while self._is_recording:
                try:
                    frame = self._capture_frame()
                    if frame is not None:
                        self._video_writer.write(frame)
                        frame_count += 1

                    # Обновление прогресса
                    current_time = time.time()
                    if current_time - last_progress_time >= 1.0:
                        duration = current_time - start_time
                        fps = frame_count / duration if duration > 0 else 0
                        self._emit(RecorderEvents.ON_PROGRESS, {
                            'frames': frame_count,
                            'fps': fps,
                            'duration': duration
                        })
                        last_progress_time = current_time

                    time.sleep(0.001)
                except Exception as e:
                    logger.error(f"Ошибка в цикле записи: {e}")
                    self._emit(RecorderEvents.ON_ERROR, str(e))
                    break

            # Остановка аудио
            if self._audio_stream:
                self._audio_stream.stop()
                self._audio_stream.close()
                self._audio_stream = None

            # Освобождение видео
            if self._video_writer:
                self._video_writer.release()
                self._video_writer = None

            # Сохранение аудио
            self._save_audio(timestamp, temp_video_file)

            logger.info("Запись завершена")

        except Exception as e:
            logger.error(f"Ошибка записи: {e}")
            self._emit(RecorderEvents.ON_ERROR, str(e))
            self._is_recording = False

    def _create_video_writer(self, path: str, width: int, height: int) -> cv2.VideoWriter:
        """Создание VideoWriter"""
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = self.settings.get('video_fps')
        writer = cv2.VideoWriter(path, fourcc, fps, (width, height))

        if not writer.isOpened():
            raise RuntimeError("Не удалось создать VideoWriter")

        return writer

    def _capture_frame(self) -> Optional[np.ndarray]:
        """Захват кадра экрана"""
        try:
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"Ошибка захвата кадра: {e}")
            return None

    def _setup_audio_stream(self) -> Optional[sd.InputStream]:
        """Настройка аудио потока"""
        device = self.settings.get('audio_device')
        sample_rate = self.settings.get('audio_sample_rate')
        channels = self.settings.get('audio_channels')

        # Автоматический поиск устройства
        if device is None:
            device = self._find_audio_device()

        if device is not None:
            try:
                stream = sd.InputStream(
                    samplerate=sample_rate,
                    channels=channels,
                    device=device,
                    callback=self._audio_callback
                )
                stream.start()
                logger.info(f"Аудио поток запущен (устройство: {device})")
                return stream
            except Exception as e:
                logger.error(f"Ошибка запуска аудио: {e}")
                return None

        logger.warning("Аудио устройство не найдено")
        return None

    def _find_audio_device(self) -> Optional[int]:
        """Поиск аудио устройства"""
        try:
            devices = sd.query_devices()

            # Поиск loopback устройств
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    name = dev['name'].lower()
                    if any(k in name for k in ['loopback', 'stereo mix', 'what u hear']):
                        logger.info(f"Найдено устройство: {dev['name']}")
                        return i

            # Если loopback не найден, берем устройство по умолчанию
            default_device = sd.default.device[0]
            if default_device is not None:
                logger.info(f"Использую устройство по умолчанию: {default_device}")
                return default_device

        except Exception as e:
            logger.error(f"Ошибка поиска устройства: {e}")
        return None

    def _audio_callback(self, indata: np.ndarray, frames: int, time: Any, status: Any) -> None:
        """Callback для аудио"""
        if status:
            if status != sd.CallbackFlags.input_overflow:
                logger.debug(f"Аудио статус: {status}")
        if self._is_recording:
            self._audio_data.append(indata.copy())

    def _save_audio(self, timestamp: str, video_path: str) -> None:
        """Сохранение аудио"""
        if not self._audio_data or not self.settings.get('record_audio'):
            self._temp_files = (video_path, None)
            return

        try:
            temp_audio_file = os.path.join(self._temp_dir, f'temp_audio_{timestamp}.wav')

            # Объединение блоков
            audio_array = np.concatenate(self._audio_data, axis=0)

            # Шумоподавление
            if (self.settings.get('noise_reduction') and
                self._audio_processor and
                self._audio_processor.is_initialized):

                logger.info("Применение фильтра высоких частот...")
                cutoff = self.settings.get('highpass_cutoff', 80)
                audio_array = self._audio_processor.apply_highpass_filter(
                    audio_array, cutoff_freq=cutoff
                )
                logger.info("Фильтр применен")

            # Нормализация
            if self._audio_processor:
                audio_array = self._audio_processor.normalize(audio_array)

            # Сохранение
            sf.write(temp_audio_file, audio_array, self.settings.get('audio_sample_rate'))
            self._temp_files = (video_path, temp_audio_file)

            logger.info(f"Аудио сохранено: {len(audio_array)} семплов")

        except Exception as e:
            logger.error(f"Ошибка сохранения аудио: {e}")
            self._temp_files = (video_path, None)

    def save(self, output_path: Optional[str] = None) -> str:
        """
        Сохранение записи

        Args:
            output_path: Путь для сохранения (опционально)

        Returns:
            Путь к сохраненному файлу
        """
        if not self._temp_files:
            raise RuntimeError("Нет данных для сохранения")

        video_path, audio_path = self._temp_files

        if output_path is None:
            output_path = self._generate_output_path()

        # Создание директории
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"Сохранение в: {output_path}")

        # Проверка наличия аудио
        has_audio = (audio_path and os.path.exists(audio_path) and
                    self.settings.get('record_audio'))

        if has_audio and MOVIEPY_AVAILABLE:
            try:
                self._save_with_moviepy(video_path, audio_path, output_path)
            except Exception as e:
                logger.error(f"Ошибка сохранения: {e}")
                self._save_video_only(video_path, output_path)
        else:
            self._save_video_only(video_path, output_path)

        self._cleanup_temp_files()
        return output_path

    def _generate_output_path(self) -> str:
        """Генерация пути для сохранения"""
        timestamp = datetime.now().strftime("%Y-%d-%m_%H-%M-%S")
        template = self.settings.get('filename_template')
        filename = template.format(timestamp=timestamp)
        save_dir = self.settings.get('save_path')
        return os.path.join(save_dir, f"{filename}.mp4")

    def _save_with_moviepy(self, video_path: str, audio_path: str, output_path: str) -> None:
        """Сохранение через moviepy"""
        logger.info("Объединение видео и аудио через moviepy...")

        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)

        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)

        final = video.set_audio(audio)
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

        logger.info("Запись сохранена успешно")

    def _save_video_only(self, video_path: str, output_path: str) -> None:
        """Сохранение только видео"""
        logger.info("Сохранение видео без звука...")
        shutil.copy2(video_path, output_path)

    def _cleanup_temp_files(self) -> None:
        """Очистка временных файлов"""
        try:
            if self._temp_files:
                video_path, audio_path = self._temp_files
                if audio_path and os.path.exists(audio_path):
                    os.remove(audio_path)
                if os.path.exists(video_path):
                    os.remove(video_path)

            if os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir)

        except Exception as e:
            logger.warning(f"Ошибка очистки временных файлов: {e}")

    def _emit(self, event: str, data: Any = None) -> None:
        """Вызов колбэков"""
        for callback in self._callbacks.get(event, []):
            try:
                if data is not None:
                    callback(data)
                else:
                    callback()
            except Exception as e:
                logger.error(f"Ошибка в callback {event}: {e}")
