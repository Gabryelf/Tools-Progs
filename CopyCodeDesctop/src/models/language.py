"""
Модель языка программирования
"""

from dataclasses import dataclass, field
from typing import Set, Dict, Optional


@dataclass
class Language:
    """Модель языка программирования"""

    name: str
    extensions: Set[str] = field(default_factory=set)
    comment_single: Optional[str] = None
    comment_multi: Optional[tuple] = None

    def matches_extension(self, extension: str) -> bool:
        """Проверка, соответствует ли расширение языку"""
        return extension in self.extensions

    def get_extensions(self) -> Set[str]:
        """Получение всех расширений"""
        return self.extensions


class LanguageRegistry:
    """Реестр языков программирования"""

    def __init__(self):
        self._languages: Dict[str, Language] = {}
        self._all_extensions: Set[str] = set()
        self._initialize_languages()

    def _initialize_languages(self) -> None:
        """Инициализация языков"""
        languages = {
            'python': Language(
                name='python',
                extensions={'.py', '.pyw', '.pyi'},
                comment_single='#',
                comment_multi=("'''", '"""')
            ),
            'javascript': Language(
                name='javascript',
                extensions={'.js', '.jsx', '.mjs', '.ts', '.tsx'},
                comment_single='//',
                comment_multi=('/*', '*/')
            ),
            'html': Language(
                name='html',
                extensions={'.html', '.htm', '.xhtml'},
                comment_multi=('<!--', '-->')
            ),
            'css': Language(
                name='css',
                extensions={'.css', '.scss', '.sass', '.less'},
                comment_multi=('/*', '*/')
            ),
            'cpp': Language(
                name='cpp',
                extensions={'.cpp', '.cc', '.cxx', '.hpp', '.hh', '.hxx'},
                comment_single='//',
                comment_multi=('/*', '*/')
            ),
            'c': Language(
                name='c',
                extensions={'.c', '.h'},
                comment_single='//',
                comment_multi=('/*', '*/')
            ),
            'java': Language(
                name='java',
                extensions={'.java', '.kt', '.kts'},
                comment_single='//',
                comment_multi=('/*', '*/')
            )
        }

        self._languages = languages

        # Собираем все расширения
        for lang in languages.values():
            self._all_extensions.update(lang.extensions)

    def get_language(self, name: str) -> Optional[Language]:
        """Получение языка по имени"""
        return self._languages.get(name)

    def get_all_languages(self) -> Dict[str, Language]:
        """Получение всех языков"""
        return self._languages.copy()

    def get_all_extensions(self) -> Set[str]:
        """Получение всех расширений"""
        return self._all_extensions.copy()

    def detect_language(self, extension: str) -> Optional[Language]:
        """Определение языка по расширению"""
        for lang in self._languages.values():
            if extension in lang.extensions:
                return lang
        return None

    def get_language_names(self) -> list:
        """Получение списка имен языков"""
        return list(self._languages.keys())


# Синглтон реестра
_registry: Optional[LanguageRegistry] = None


def get_language_registry() -> LanguageRegistry:
    """Получение экземпляра реестра языков"""
    global _registry
    if _registry is None:
        _registry = LanguageRegistry()
    return _registry
