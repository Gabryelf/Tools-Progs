"""
Пользовательские исключения
"""


class CopyCodeError(Exception):
    """Базовое исключение приложения"""
    pass


class ProjectNotFoundError(CopyCodeError):
    """Исключение: проект не найден"""
    pass


class FileProcessingError(CopyCodeError):
    """Исключение: ошибка обработки файла"""
    pass


class ClipboardError(CopyCodeError):
    """Исключение: ошибка работы с буфером обмена"""
    pass


class ConfigurationError(CopyCodeError):
    """Исключение: ошибка конфигурации"""
    pass
