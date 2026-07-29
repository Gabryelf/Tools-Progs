"""
Сервис для сбора кода из проекта с поддержкой внешних файлов
"""

from pathlib import Path
from typing import List, Set, Optional, Dict, Any
import os
from src.services.file_processor import FileProcessor
from src.services.external_files_manager import ExternalFilesManager
from src.models.language import get_language_registry
from src.models.settings import ApplicationSettings


class CodeCollector:
    """Сборщик кода проекта с поддержкой внешних файлов"""

    def __init__(self, settings: ApplicationSettings):
        """
        Инициализация сборщика

        Args:
            settings: Настройки приложения
        """
        self.settings = settings
        self.language_registry = get_language_registry()
        self.file_processor = FileProcessor(
            include_comments=settings.include_comments,
            include_empty=settings.include_empty_lines
        )
        self.files_count = 0
        self.external_files_manager = ExternalFilesManager()

    def collect(self, include_external: bool = True) -> str:
        """
        Сборка всего кода из проекта и внешних файлов

        Args:
            include_external: Включать ли внешние файлы

        Returns:
            str: Собранный код
        """
        self.files_count = 0

        if not self.settings.project_path.exists():
            return f"❌ Папка '{self.settings.project_path}' не существует"

        # Получаем расширения для выбранного языка
        extensions = self._get_extensions()
        ignore_dirs = self.settings.ignore_dirs
        ignore_patterns = self._get_ignore_patterns()

        result = []

        # Добавляем структуру проекта
        if self.settings.include_structure:
            result.extend(self._build_structure(extensions, ignore_dirs))

        # Собираем содержимое файлов проекта
        result.extend(self._collect_files(
            extensions, ignore_dirs, ignore_patterns
        ))

        # Добавляем внешние файлы
        if include_external and self.external_files_manager.get_files_count() > 0:
            result.extend(self._collect_external_files())

        return '\n'.join(result)

    def _get_extensions(self) -> Set[str]:
        """Получение расширений для выбранного языка"""
        if self.settings.language == 'all':
            return self.language_registry.get_all_extensions()

        language = self.language_registry.get_language(self.settings.language)
        if language:
            return language.get_extensions()

        return set()

    def _get_ignore_patterns(self) -> List[str]:
        """Получение паттернов для игнорирования"""
        return ['*.pyc', '*.pyo', '*.so', '*.dll', '*.exe', '*.log']

    def _build_structure(self, extensions: Set[str], ignore_dirs: List[str]) -> List[str]:
        """Построение структуры проекта"""
        result = [
            "📁 СТРУКТУРА ПРОЕКТА",
            "=" * 80
        ]

        for root, dirs, files in os.walk(self.settings.project_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]

            level = root.replace(str(self.settings.project_path), '').count(os.sep)
            indent = '  ' * level

            result.append(f"{indent}📁 {Path(root).name}/")

            for file in sorted(files):
                if Path(file).suffix in extensions:
                    result.append(f"{indent}  📄 {file}")
                    self.files_count += 1

        result.extend(["", "=" * 80, ""])
        return result

    def _collect_files(
        self,
        extensions: Set[str],
        ignore_dirs: List[str],
        ignore_patterns: List[str]
    ) -> List[str]:
        """Сбор содержимого файлов проекта"""
        result = []

        for root, dirs, files in os.walk(self.settings.project_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]

            for file in files:
                file_path = Path(root) / file

                if file_path.suffix not in extensions:
                    continue

                if self.file_processor.should_ignore_file(file_path, ignore_patterns):
                    continue

                relative_path = file_path.relative_to(self.settings.project_path)

                result.extend([
                    "",
                    "-" * 80,
                    f"📄 {relative_path}",
                    "-" * 80
                ])

                content = self.file_processor.process_file(file_path)
                result.extend(content if content else ["# (файл пуст)"])

                self.files_count += 1

        return result

    def _collect_external_files(self) -> List[str]:
        """Сбор содержимого внешних файлов"""
        result = []

        result.extend([
            "",
            "=" * 80,
            "📎 ВНЕШНИЕ ФАЙЛЫ (добавлены из других папок)",
            "=" * 80
        ])

        external_contents = self.external_files_manager.get_file_contents()

        for file_name, content in external_contents.items():
            result.extend([
                "",
                "-" * 80,
                f"📎 {file_name} (внешний файл)",
                "-" * 80
            ])

            # Разбиваем содержимое на строки и добавляем
            lines = content.split('\n')
            result.extend(lines)

        return result

    def get_files_count(self) -> int:
        """Получение количества обработанных файлов"""
        return self.files_count

    def get_external_files_count(self) -> int:
        """Получение количества внешних файлов"""
        return self.external_files_manager.get_files_count()

    def add_external_file(self, file_path: Path) -> bool:
        """Добавление внешнего файла"""
        return self.external_files_manager.add_file(file_path)

    def remove_external_file(self, index: int) -> bool:
        """Удаление внешнего файла"""
        return self.external_files_manager.remove_file(index)

    def clear_external_files(self):
        """Очистка внешних файлов"""
        self.external_files_manager.clear_files()

    def get_external_files(self) -> List[Dict[str, str]]:
        """Получение списка внешних файлов"""
        return self.external_files_manager.get_files()
