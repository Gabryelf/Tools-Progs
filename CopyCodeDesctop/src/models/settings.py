"""
Модель настроек приложения
"""

from dataclasses import dataclass, field
from typing import List, Set, Optional
from pathlib import Path


@dataclass
class ApplicationSettings:
    """Настройки приложения"""

    # Пути
    project_path: Path = field(default_factory=Path.cwd)
    config_path: Path = field(default_factory=lambda: Path.home() / ".copycode_settings.json")

    # Настройки кода
    language: str = "all"
    include_comments: bool = True
    include_empty_lines: bool = False
    include_structure: bool = True

    # Игнорирование
    ignore_dirs: List[str] = field(default_factory=lambda: [
        "__pycache__", ".git", "node_modules", "venv", ".idea", ".vscode"
    ])

    # UI
    window_width: int = 650
    window_height: int = 600
    theme: str = "default"

    def __post_init__(self):
        """Загрузка сохраненных настроек"""
        self.load()

    def load(self) -> None:
        """Загрузка настроек из файла"""
        try:
            if self.config_path.exists():
                import json
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self, key):
                            # Преобразуем строку пути обратно в Path
                            if key == 'project_path' and value:
                                setattr(self, key, Path(value))
                            else:
                                setattr(self, key, value)
        except Exception:
            pass

    def save(self) -> None:
        """Сохранение настроек в файл"""
        try:
            import json
            data = {
                'project_path': str(self.project_path),
                'language': self.language,
                'include_comments': self.include_comments,
                'include_empty_lines': self.include_empty_lines,
                'include_structure': self.include_structure,
                'ignore_dirs': self.ignore_dirs,
                'window_width': self.window_width,
                'window_height': self.window_height,
                'theme': self.theme
            }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения настроек: {e}")
