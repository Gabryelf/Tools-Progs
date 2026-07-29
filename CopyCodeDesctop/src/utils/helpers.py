"""
Вспомогательные функции
"""

import os
from pathlib import Path
from typing import List, Optional
import re


def get_file_size_str(size_bytes: int) -> str:
    """
    Преобразование размера в читаемый формат

    Args:
        size_bytes: Размер в байтах

    Returns:
        str: Строка с размером
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_extension_from_path(file_path: Path) -> str:
    """
    Получение расширения файла с точкой

    Args:
        file_path: Путь к файлу

    Returns:
        str: Расширение файла
    """
    return file_path.suffix.lower()


def is_binary_file(file_path: Path, sample_size: int = 1024) -> bool:
    """
    Проверка, является ли файл бинарным

    Args:
        file_path: Путь к файлу
        sample_size: Размер выборки для проверки

    Returns:
        bool: True если файл бинарный
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(sample_size)
            return b'\0' in chunk
    except:
        return True


def get_language_from_extension(extension: str) -> Optional[str]:
    """
    Определение языка по расширению

    Args:
        extension: Расширение файла

    Returns:
        Optional[str]: Название языка
    """
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'javascript',
        '.html': 'html',
        '.css': 'css',
        '.c': 'c',
        '.cpp': 'cpp',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust'
    }
    return extension_map.get(extension)


def sanitize_filename(filename: str) -> str:
    """
    Очистка имени файла от недопустимых символов

    Args:
        filename: Имя файла

    Returns:
        str: Очищенное имя
    """
    # Удаляем недопустимые символы для Windows
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def ensure_directory(path: Path) -> Path:
    """
    Создание директории если её нет

    Args:
        path: Путь к директории

    Returns:
        Path: Созданный путь
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_name(path: Path) -> str:
    """
    Получение имени проекта из пути

    Args:
        path: Путь к проекту

    Returns:
        str: Имя проекта
    """
    return path.name


def format_timestamp() -> str:
    """
    Получение отформатированной временной метки

    Returns:
        str: Временная метка
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
