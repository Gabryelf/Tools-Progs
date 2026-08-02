"""
Константы приложения
"""
import os
from pathlib import Path

# Информация о приложении
APP_NAME = "Screen Recorder"
APP_VERSION = "0.0.5"
APP_AUTHOR = "Gabryelf"
APP_DESCRIPTION = "Запись экрана с системным звуком"
APP_COPYRIGHT = f"Copyright © {APP_AUTHOR} 2026"
APP_LICENSE = "MIT License"
APP_HOMEPAGE = "https://github.com/Gabryelf/Tools-Progs"

# Пути
BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config"
ASSETS_DIR = BASE_DIR / "assets"
LOGS_DIR = Path.home() / ".screen_recorder" / "logs"

# Настройки по умолчанию
DEFAULT_SAVE_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
DEFAULT_FILENAME_TEMPLATE = "Запись_экрана_{timestamp}"
DEFAULT_VIDEO_FPS = 20
DEFAULT_AUDIO_SAMPLE_RATE = 48000
DEFAULT_AUDIO_CHANNELS = 2
DEFAULT_NOISE_REDUCTION = True
DEFAULT_HIGHPASS_CUTOFF = 80

# Форматы
VIDEO_CODEC = 'XVID'
AUDIO_CODEC = 'aac'
CONTAINER_FORMAT = 'mp4'

# Временные файлы
TEMP_VIDEO_PREFIX = "temp_video"
TEMP_AUDIO_PREFIX = "temp_audio"

# Настройки интерфейса
WINDOW_WIDTH = 450
WINDOW_HEIGHT = 650
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 600
COMPACT_HEIGHT = 80
COMPACT_WIDTH = 400

# Иконки
ICON_PATH = ASSETS_DIR / "icon.ico"
TRAY_ICON_PATH = ASSETS_DIR / "tray_icon.png"