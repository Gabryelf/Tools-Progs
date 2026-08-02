"""
Модуль для работы с настройками
"""
import json
import os
import logging
from dataclasses import dataclass, asdict
from typing import Optional, Any

from constants import (
    DEFAULT_SAVE_PATH,
    DEFAULT_FILENAME_TEMPLATE,
    DEFAULT_VIDEO_FPS,
    DEFAULT_AUDIO_SAMPLE_RATE,
    DEFAULT_AUDIO_CHANNELS,
    DEFAULT_NOISE_REDUCTION,
    DEFAULT_HIGHPASS_CUTOFF,
    CONFIG_DIR
)

logger = logging.getLogger(__name__)


@dataclass
class RecorderSettings:
    """Настройки записи"""
    # Аудио
    audio_device: Optional[int] = None
    audio_sample_rate: int = DEFAULT_AUDIO_SAMPLE_RATE
    audio_channels: int = DEFAULT_AUDIO_CHANNELS
    record_audio: bool = True

    # Шумоподавление
    noise_reduction: bool = DEFAULT_NOISE_REDUCTION
    highpass_cutoff: int = DEFAULT_HIGHPASS_CUTOFF

    # Видео
    video_fps: int = DEFAULT_VIDEO_FPS

    # Сохранение
    save_path: str = DEFAULT_SAVE_PATH
    filename_template: str = DEFAULT_FILENAME_TEMPLATE

    # Интерфейс
    show_fps: bool = True
    show_preview: bool = False

    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'RecorderSettings':
        """Создание из словаря"""
        return cls(**data)


class SettingsManager:
    """Менеджер настроек"""

    def __init__(self, config_file: str = None):
        self.config_file = config_file or str(CONFIG_DIR / "settings.json")
        self.settings = RecorderSettings()
        self._load()

    def _load(self) -> None:
        """Загрузка настроек из файла"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.settings, key):
                            setattr(self.settings, key, value)
                logger.info(f"Настройки загружены из {self.config_file}")
        except Exception as e:
            logger.warning(f"Не удалось загрузить настройки: {e}")

    def save(self) -> None:
        """Сохранение настроек в файл"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, indent=4, ensure_ascii=False)
            logger.info(f"Настройки сохранены в {self.config_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение настройки"""
        return getattr(self.settings, key, default)

    def set(self, key: str, value: Any) -> None:
        """Установить значение настройки"""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
            self.save()
        else:
            logger.warning(f"Неизвестная настройка: {key}")

    def reset_to_defaults(self) -> None:
        """Сброс настроек к значениям по умолчанию"""
        self.settings = RecorderSettings()
        self.save()