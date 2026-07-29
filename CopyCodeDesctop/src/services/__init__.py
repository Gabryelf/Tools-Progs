"""
Сервисы приложения
"""

from src.services.code_collector import CodeCollector
from src.services.file_processor import FileProcessor
from src.services.clipboard_manager import ClipboardManager

__all__ = [
    'CodeCollector',
    'FileProcessor',
    'ClipboardManager'
]