"""
Сервис для сбора кода из проекта
"""

from pathlib import Path
from typing import List, Set, Optional, Dict, Any
import os
from ..services.file_processor import FileProcessor
from ..models.language import get_language_registry
from ..models.settings import ApplicationSettings


class CodeCollector:
    """Сборщик кода проекта"""

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

    def collect(self) -> str:
        """
        Сборка всего кода из проекта

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

        # Собираем содержимое файлов
        result.extend(self._collect_files(
            extensions, ignore_dirs, ignore_patterns
        ))

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
        # Можно загрузить из конфига
        return ['*.pyc', '*.pyo', '*.so', '*.dll', '*.exe', '*.log']

    def _build_structure(self, extensions: Set[str], ignore_dirs: List[str]) -> List[str]:
        """
        Построение структуры проекта

        Args:
            extensions: Расширения файлов для отображения
            ignore_dirs: Игнорируемые папки

        Returns:
            List[str]: Строки структуры
        """
        result = [
            "📁 СТРУКТУРА ПРОЕКТА",
            "=" * 80
        ]

        for root, dirs, files in os.walk(self.settings.project_path):
            # Фильтруем папки
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
        """
        Сбор содержимого файлов

        Args:
            extensions: Расширения для сбора
            ignore_dirs: Игнорируемые папки
            ignore_patterns: Паттерны игнорирования

        Returns:
            List[str]: Строки с кодом
        """
        result = []
        self.files_count = 0

        for root, dirs, files in os.walk(self.settings.project_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]

            for file in files:
                file_path = Path(root) / file

                # Проверяем расширение
                if file_path.suffix not in extensions:
                    continue

                # Проверяем паттерны игнорирования
                if self.file_processor.should_ignore_file(file_path, ignore_patterns):
                    continue

                relative_path = file_path.relative_to(self.settings.project_path)

                # Добавляем заголовок файла
                result.extend([
                    "",
                    "-" * 80,
                    f"📄 {relative_path}",
                    "-" * 80
                ])

                # Обрабатываем файл
                content = self.file_processor.process_file(file_path)
                result.extend(content if content else ["# (файл пуст)"])

                self.files_count += 1

        return result

    def get_files_count(self) -> int:
        """Получение количества обработанных файлов"""
        return self.files_count
