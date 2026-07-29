"""
Модуль для управления конфигурацией приложения
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    """Класс конфигурации приложения"""

    # Пути
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    config_path: Path = field(default=None)

    # Секции конфига
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Инициализация после создания"""
        if self.config_path is None:
            self.config_path = self.base_dir / "config" / "settings.json"
        self.load()

    def load(self) -> None:
        """Загрузка конфигурации из файла"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = self._create_default_config()
                self.save()
        except Exception as e:
            print(f"⚠️ Ошибка загрузки конфига: {e}")
            self.data = self._create_default_config()

    def save(self) -> None:
        """Сохранение конфигурации в файл"""
        try:
            # Создаем папку если её нет
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения конфига: {e}")

    def _create_default_config(self) -> Dict[str, Any]:
        """Создание дефолтной конфигурации"""
        return {
            "app": {
                "name": "Copy Code Pro",
                "version": "0.0.2",
                "author": "Gabryelf"
            },
            "paths": {
                "icons": "assets/icons"
            },
            "ui": {
                "window_width": 650,
                "window_height": 600
            },
            "code": {
                "max_file_size_mb": 5,
                "include_comments": True,
                "include_empty_lines": False,
                "include_structure": True
            },
            "ignore": {
                "directories": ["__pycache__", ".git", "node_modules", "venv"],
                "files": ["*.pyc", "*.pyo"]
            },
            "languages": {
                "python": [".py", ".pyw"],
                "javascript": [".js", ".jsx", ".ts", ".tsx"],
                "html": [".html", ".htm"],
                "css": [".css", ".scss"],
                "cpp": [".cpp", ".h", ".hpp"]
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения по ключу (с поддержкой вложенности)"""
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Установка значения по ключу"""
        keys = key.split('.')
        data = self.data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value
        self.save()

    @property
    def icon_path(self) -> Path:
        """Путь к папке с иконками"""
        return self.base_dir / self.get('paths.icons', 'assets/icons')

    @property
    def ignore_dirs(self) -> list:
        """Список игнорируемых папок"""
        return self.get('ignore.directories', [])

    @property
    def languages(self) -> Dict[str, list]:
        """Словарь языков и их расширений"""
        return self.get('languages', {})

    @property
    def max_file_size(self) -> int:
        """Максимальный размер файла в байтах"""
        return self.get('code.max_file_size_mb', 5) * 1024 * 1024


# Синглтон конфигурации
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Получение экземпляра конфигурации"""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config
