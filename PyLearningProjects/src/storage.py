""" =========================================================
        Сохранение и загрузка задач в JSON.
    =========================================================
"""
import json
from config import NAME_FILE_SAVES


def load_collection(file_name=NAME_FILE_SAVES):
    """Загрузить список задач из файла. Возвращает list[dict]."""
    with open(file_name, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return []

    result = []
    for item in data:
        if isinstance(item, dict):
            result.append({
                "name": item.get("name", ""),
                "content": item.get("content", ""),
            })
    return result


def save_collection(collection, file_name=NAME_FILE_SAVES):
    """Сохранить список задач в файл."""
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(collection, file, ensure_ascii=False, indent=2)
