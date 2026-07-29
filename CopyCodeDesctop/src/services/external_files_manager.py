"""
Менеджер внешних файлов для добавления файлов из других папок
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import json


class ExternalFilesManager:
    """Менеджер для работы с внешними файлами"""

    def __init__(self):
        self.external_files: List[Dict[str, str]] = []
        self.settings_file = Path.home() / ".copycode_external_files.json"
        self.load_settings()

    def add_file(self, file_path: Path) -> bool:
        """
        Добавление внешнего файла в список

        Args:
            file_path: Путь к файлу

        Returns:
            bool: True если файл добавлен
        """
        if not file_path.exists():
            return False

        # Проверяем, не добавлен ли уже
        for item in self.external_files:
            if item['path'] == str(file_path):
                return False

        # Добавляем файл
        self.external_files.append({
            'path': str(file_path),
            'name': file_path.name,
            'size': file_path.stat().st_size
        })

        self.save_settings()
        return True

    def remove_file(self, index: int) -> bool:
        """
        Удаление внешнего файла из списка

        Args:
            index: Индекс файла в списке

        Returns:
            bool: True если файл удален
        """
        if 0 <= index < len(self.external_files):
            del self.external_files[index]
            self.save_settings()
            return True
        return False

    def clear_files(self):
        """Очистка списка внешних файлов"""
        self.external_files.clear()
        self.save_settings()

    def get_files(self) -> List[Dict[str, str]]:
        """Получение списка внешних файлов"""
        return self.external_files.copy()

    def get_file_contents(self) -> Dict[str, str]:
        """
        Получение содержимого всех внешних файлов

        Returns:
            Dict[str, str]: Словарь {имя_файла: содержимое}
        """
        contents = {}
        for item in self.external_files:
            file_path = Path(item['path'])
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    contents[item['name']] = f.read()
            except Exception as e:
                contents[item['name']] = f"# ❌ Ошибка чтения: {e}"
        return contents

    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.external_files = data.get('external_files', [])
        except Exception:
            pass

    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'external_files': self.external_files
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения внешних файлов: {e}")

    def get_files_count(self) -> int:
        """Получение количества внешних файлов"""
        return len(self.external_files)