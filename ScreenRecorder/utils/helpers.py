"""
Вспомогательные функции
"""
import os
from pathlib import Path
from typing import Union


def format_time(seconds: float) -> str:
    """
    Форматирование времени

    Args:
        seconds: Время в секундах

    Returns:
        Строка в формате HH:MM:SS
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_file_size(file_path: Union[str, Path]) -> str:
    """
    Получение размера файла в читаемом формате

    Args:
        file_path: Путь к файлу

    Returns:
        Строка с размером
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return "0 B"

    size = file_path.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Создание директории, если она не существует

    Args:
        path: Путь к директории

    Returns:
        Path объект
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_timestamp() -> str:
    """
    Получение временной метки для имен файлов

    Returns:
        Строка с временной меткой
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%d-%m_%H-%M-%S")
