"""
Сервис для обработки файлов
"""

from pathlib import Path
from typing import List, Optional, Set
import re
from ..models.language import Language, get_language_registry


class FileProcessor:
    """Обработчик файлов"""

    def __init__(self, include_comments: bool = True, include_empty: bool = False):
        self.include_comments = include_comments
        self.include_empty = include_empty
        self.language_registry = get_language_registry()
        self.max_file_size = 5 * 1024 * 1024  # 5 MB по умолчанию

    def process_file(self, file_path: Path, max_size: int = None) -> List[str]:
        """
        Обработка файла и возврат списка строк

        Args:
            file_path: Путь к файлу
            max_size: Максимальный размер файла в байтах

        Returns:
            List[str]: Обработанные строки
        """
        if max_size is None:
            max_size = self.max_file_size

        # Проверка размера
        if file_path.stat().st_size > max_size:
            return [f"# ⚠️ Файл слишком большой ({file_path.stat().st_size // 1024} KB)"]

        # Определяем язык
        language = self.language_registry.detect_language(file_path.suffix)

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            return self._process_content(content, language)
        except Exception as e:
            return [f"# ❌ Ошибка чтения: {e}"]

    def _process_content(self, content: str, language: Optional[Language]) -> List[str]:
        """
        Обработка содержимого файла

        Args:
            content: Содержимое файла
            language: Язык программирования

        Returns:
            List[str]: Обработанные строки
        """
        lines = content.splitlines()
        processed = []

        # Определяем маркеры комментариев
        multiline_start, multiline_end = None, None
        if language and language.comment_multi:
            multiline_start, multiline_end = language.comment_multi

        in_multiline = False

        for line in lines:
            original_line = line.rstrip()

            # Проверка на многострочные комментарии
            if multiline_start and multiline_end:
                if multiline_start in original_line:
                    in_multiline = not in_multiline
                    if not self.include_comments:
                        continue

                if in_multiline and not self.include_comments:
                    continue

            # Пропускаем пустые строки
            if not self.include_empty and not original_line.strip():
                continue

            # Удаляем однострочные комментарии
            if not self.include_comments:
                clean_line = self._remove_single_line_comments(original_line, language)
            else:
                clean_line = original_line

            if clean_line or self.include_empty:
                processed.append(clean_line)

        return processed

    def _remove_single_line_comments(self, line: str, language: Optional[Language]) -> str:
        """
        Удаление однострочных комментариев

        Args:
            line: Строка кода
            language: Язык программирования

        Returns:
            str: Строка без комментариев
        """
        if language and language.comment_single:
            comment_marker = language.comment_single
            if comment_marker in line:
                # Учитываем строки в кавычках
                parts = line.split(comment_marker)
                # Проверяем, не внутри ли строки
                if len(parts) > 1:
                    # Простая проверка: если нечетное количество кавычек до комментария
                    before = parts[0]
                    if before.count('"') % 2 == 0 and before.count("'") % 2 == 0:
                        return before.rstrip()
        return line

    def should_ignore_file(self, file_path: Path, ignore_patterns: List[str]) -> bool:
        """
        Проверка, нужно ли игнорировать файл

        Args:
            file_path: Путь к файлу
            ignore_patterns: Список паттернов для игнорирования

        Returns:
            bool: True если файл нужно игнорировать
        """
        for pattern in ignore_patterns:
            if pattern.startswith('*'):
                if file_path.suffix == pattern[1:]:
                    return True
            elif pattern in str(file_path):
                return True
        return False

    def set_max_file_size(self, size_mb: int) -> None:
        """Установка максимального размера файла"""
        self.max_file_size = size_mb * 1024 * 1024
