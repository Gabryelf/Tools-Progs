# screen_recorder/core/settings.py
"""
Модуль для работы с настройками
"""
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class RecorderSettings:
    """Настройки записи"""
    # Звук
    audio_device: Optional[int] = None
    audio_sample_rate: int = 48000
    audio_channels: int = 2
    record_audio: bool = True

    # Шумоподавление
    noise_reduction: bool = True

    # Видео
    video_fps: int = 20
    video_codec: str = 'mp4v'

    # Сохранение
    save_path: str = os.path.join(os.path.expanduser("~"), "Desktop")
    filename_template: str = "Запись_экрана_{timestamp}"

    # Интерфейс
    show_fps: bool = True
    show_preview: bool = False


class SettingsManager:
    """Менеджер настроек"""

    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = config_file
        self.settings = RecorderSettings()
        self.load()

    def load(self):
        """Загрузка настроек из файла"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.settings, key):
                            setattr(self.settings, key, value)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки настроек: {e}")

    def save(self):
        """Сохранение настроек в файл"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения настроек: {e}")

    def get(self, key: str):
        """Получить значение настройки"""
        return getattr(self.settings, key, None)

    def set(self, key: str, value):
        """Установить значение настройки"""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
            self.save()
            