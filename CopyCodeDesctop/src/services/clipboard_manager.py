"""
Сервис для работы с буфером обмена
"""

import sys
import subprocess
from typing import Optional


class ClipboardManager:
    """Менеджер буфера обмена"""

    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """
        Копирование текста в буфер обмена

        Args:
            text: Текст для копирования

        Returns:
            bool: True если успешно
        """
        try:
            # Пробуем использовать pyperclip
            try:
                import pyperclip
                pyperclip.copy(text)
                return True
            except ImportError:
                pass

            # Windows
            if sys.platform == 'win32':
                return ClipboardManager._copy_windows(text)

            # Linux
            elif sys.platform.startswith('linux'):
                return ClipboardManager._copy_linux(text)

            # MacOS
            elif sys.platform == 'darwin':
                return ClipboardManager._copy_macos(text)

            return False

        except Exception as e:
            print(f"⚠️ Ошибка копирования: {e}")
            return False

    @staticmethod
    def _copy_windows(text: str) -> bool:
        """Копирование в Windows через clip"""
        try:
            process = subprocess.Popen(
                ['clip'],
                stdin=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            process.communicate(text.encode('utf-8'))
            return True
        except:
            return False

    @staticmethod
    def _copy_linux(text: str) -> bool:
        """Копирование в Linux"""
        try:
            # Пробуем xclip
            process = subprocess.Popen(
                ['xclip', '-selection', 'clipboard'],
                stdin=subprocess.PIPE
            )
            process.communicate(text.encode('utf-8'))
            return True
        except:
            try:
                # Пробуем xsel
                process = subprocess.Popen(
                    ['xsel', '--clipboard', '--input'],
                    stdin=subprocess.PIPE
                )
                process.communicate(text.encode('utf-8'))
                return True
            except:
                return False

    @staticmethod
    def _copy_macos(text: str) -> bool:
        """Копирование в MacOS"""
        try:
            process = subprocess.Popen(
                ['pbcopy'],
                stdin=subprocess.PIPE
            )
            process.communicate(text.encode('utf-8'))
            return True
        except:
            return False

    @staticmethod
    def get_from_clipboard() -> Optional[str]:
        """Получение текста из буфера обмена"""
        try:
            import pyperclip
            return pyperclip.paste()
        except:
            return None
