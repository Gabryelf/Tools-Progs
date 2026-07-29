"""
Пользовательские виджеты для интерфейса
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional, Callable, Union

try:
    from PIL import Image, ImageTk
except ImportError:
    print("⚠️ Установите: pip install Pillow")
    raise

# Импортируем наш SVG рендерер
from src.ui.svg_renderer import IconManagerWithSVG as IconManager


class IconButton(ttk.Button):
    """Кнопка с иконкой (поддерживает SVG)"""

    def __init__(self, parent, icon_path: Optional[Path] = None,
                 text: str = "", command: Callable = None,
                 icon_size: tuple = (20, 20), **kwargs):
        super().__init__(parent, text=text, command=command, **kwargs)
        self.icon_path = icon_path
        self.icon_size = icon_size
        self._photo = None
        self._load_icon()

    def _load_icon(self):
        if self.icon_path:
            photo = IconManager.load_icon(self.icon_path, self.icon_size)
            if photo:
                self._photo = photo
                self.config(image=photo, compound=tk.LEFT)
            else:
                # Если иконка не загрузилась, показываем текст
                print(f"⚠️ Иконка не загружена: {self.icon_path}")

    def set_icon(self, icon_path: Path, size: tuple = None):
        self.icon_path = icon_path
        if size:
            self.icon_size = size
        self._load_icon()


class IconLabel(ttk.Label):
    """Метка с иконкой (поддерживает SVG)"""

    def __init__(self, parent, icon_path: Optional[Path] = None,
                 text: str = "", icon_size: tuple = (20, 20), **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self.icon_path = icon_path
        self.icon_size = icon_size
        self._photo = None
        self._load_icon()

    def _load_icon(self):
        if self.icon_path:
            photo = IconManager.load_icon(self.icon_path, self.icon_size)
            if photo:
                self._photo = photo
                self.config(image=photo, compound=tk.LEFT)
            else:
                print(f"⚠️ Иконка не загружена: {self.icon_path}")

    def set_icon(self, icon_path: Path, size: tuple = None):
        self.icon_path = icon_path
        if size:
            self.icon_size = size
        self._load_icon()


class FileSelector(ttk.Frame):
    """Виджет выбора файла/папки"""

    def __init__(self, parent, label: str = "Выберите папку:",
                 on_select: Callable = None, icon_path: Optional[Path] = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.on_select = on_select
        self.path_var = tk.StringVar()

        if icon_path and icon_path.exists():
            self.icon_label = IconLabel(self, icon_path=icon_path, icon_size=(20, 20))
            self.icon_label.pack(side=tk.LEFT, padx=2)

        ttk.Label(self, text=label).pack(side=tk.LEFT, padx=5)

        self.entry = ttk.Entry(self, textvariable=self.path_var, width=50)
        self.entry.pack(side=tk.LEFT, padx=5)

        self.browse_btn = ttk.Button(
            self,
            text="Обзор...",
            command=self._browse
        )
        self.browse_btn.pack(side=tk.LEFT, padx=5)

    def _browse(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
            if self.on_select:
                self.on_select(Path(folder))

    def get_path(self) -> Path:
        return Path(self.path_var.get())

    def set_path(self, path: Path):
        self.path_var.set(str(path))


class LanguageSelector(ttk.LabelFrame):
    """Виджет выбора языка с иконками"""

    def __init__(self, parent, languages: list,
                 on_select: Callable = None,
                 icons_dir: Optional[Path] = None,
                 **kwargs):
        super().__init__(parent, text="Выберите язык:", **kwargs)
        self.on_select = on_select
        self.language_var = tk.StringVar(value="all")
        self.icons_dir = icons_dir
        self._create_language_buttons(languages)

    def _find_icon(self, name: str) -> Optional[Path]:
        """Поиск иконки по имени"""
        if not self.icons_dir:
            return None

        # Ищем по разным расширениям
        for ext in ['.svg', '.png', '.ico']:
            path = self.icons_dir / f"{name}{ext}"
            if path.exists():
                return path

        # Пробуем альтернативные имена
        alternatives = {
            'all': ['language', 'code'],
            'python': ['py', 'snake'],
            'javascript': ['js', 'node'],
            'html': ['htm', 'web'],
            'css': ['style'],
            'c': ['clang'],
            'cpp': ['cplusplus', 'c++'],
            'java': ['coffee'],
            'go': ['golang'],
            'rust': ['crab']
        }

        if name in alternatives:
            for alt in alternatives[name]:
                for ext in ['.svg', '.png', '.ico']:
                    path = self.icons_dir / f"{alt}{ext}"
                    if path.exists():
                        return path

        return None

    def _create_language_buttons(self, languages: list):
        row, col = 0, 0

        for lang in languages:
            frame = ttk.Frame(self)
            frame.grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)

            icon_path = self._find_icon(lang)

            if icon_path:
                icon_label = IconLabel(
                    frame,
                    icon_path=icon_path,
                    icon_size=(16, 16),
                    text=""
                )
                icon_label.pack(side=tk.LEFT, padx=(0, 5))
            else:
                # Если иконка не найдена, используем текстовый символ
                ttk.Label(frame, text="●").pack(side=tk.LEFT, padx=(0, 5))

            ttk.Radiobutton(
                frame,
                text=lang.capitalize() if lang != 'all' else 'Все',
                value=lang,
                variable=self.language_var,
                command=self._on_select,
                style='Language.TRadiobutton'
            ).pack(side=tk.LEFT)

            col += 1
            if col > 3:
                col = 0
                row += 1

    def _on_select(self):
        if self.on_select:
            self.on_select(self.language_var.get())

    def get_language(self) -> str:
        return self.language_var.get()

    def set_language(self, language: str):
        self.language_var.set(language)


class OptionsPanel(ttk.LabelFrame):
    """Панель опций с иконками"""

    def __init__(self, parent, icons_dir: Optional[Path] = None, **kwargs):
        super().__init__(parent, text="Настройки", **kwargs)
        self.icons_dir = icons_dir

        self.comments_var = tk.BooleanVar(value=True)
        self.empty_var = tk.BooleanVar(value=False)
        self.structure_var = tk.BooleanVar(value=True)

        self._create_widgets()

    def _find_icon(self, name: str) -> Optional[Path]:
        """Поиск иконки по имени"""
        if not self.icons_dir:
            return None

        # Ищем по разным расширениям
        for ext in ['.svg', '.png', '.ico']:
            path = self.icons_dir / f"{name}{ext}"
            if path.exists():
                return path

        # Пробуем альтернативные имена
        alternatives = {
            'comments': ['comment', 'text', 'note'],
            'empty': ['empty_battery', 'blank', 'space'],
            'structure': ['database', 'tree', 'folder_tree'],
            'folder': ['directory', 'open_folder']
        }

        if name in alternatives:
            for alt in alternatives[name]:
                for ext in ['.svg', '.png', '.ico']:
                    path = self.icons_dir / f"{alt}{ext}"
                    if path.exists():
                        return path

        return None

    def _create_widgets(self):
        # Комментарии
        comments_frame = ttk.Frame(self)
        comments_frame.grid(row=0, column=0, sticky=tk.W, padx=5)

        icon_path = self._find_icon('comments')
        if icon_path:
            icon_label = IconLabel(
                comments_frame,
                icon_path=icon_path,
                icon_size=(16, 16),
                text=""
            )
            icon_label.pack(side=tk.LEFT)
        else:
            ttk.Label(comments_frame, text="💬").pack(side=tk.LEFT)

        ttk.Checkbutton(
            comments_frame,
            text="Включать комментарии",
            variable=self.comments_var,
            style='Option.TCheckbutton'
        ).pack(side=tk.LEFT)

        # Пустые строки
        empty_frame = ttk.Frame(self)
        empty_frame.grid(row=0, column=1, sticky=tk.W, padx=20)

        icon_path = self._find_icon('empty')
        if icon_path:
            icon_label = IconLabel(
                empty_frame,
                icon_path=icon_path,
                icon_size=(16, 16),
                text=""
            )
            icon_label.pack(side=tk.LEFT)
        else:
            ttk.Label(empty_frame, text="⬜").pack(side=tk.LEFT)

        ttk.Checkbutton(
            empty_frame,
            text="Включать пустые строки",
            variable=self.empty_var,
            style='Option.TCheckbutton'
        ).pack(side=tk.LEFT)

        # Структура
        structure_frame = ttk.Frame(self)
        structure_frame.grid(row=0, column=2, sticky=tk.W, padx=20)

        icon_path = self._find_icon('structure')
        if icon_path:
            icon_label = IconLabel(
                structure_frame,
                icon_path=icon_path,
                icon_size=(16, 16),
                text=""
            )
            icon_label.pack(side=tk.LEFT)
        else:
            ttk.Label(structure_frame, text="📊").pack(side=tk.LEFT)

        ttk.Checkbutton(
            structure_frame,
            text="Показывать структуру",
            variable=self.structure_var,
            style='Option.TCheckbutton'
        ).pack(side=tk.LEFT)

        # Игнорируемые папки
        ignore_frame = ttk.Frame(self)
        ignore_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)

        icon_path = self._find_icon('folder')
        if icon_path:
            icon_label = IconLabel(
                ignore_frame,
                icon_path=icon_path,
                icon_size=(16, 16),
                text=""
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 5))
        else:
            ttk.Label(ignore_frame, text="📁").pack(side=tk.LEFT, padx=(0, 5))

        ttk.Label(ignore_frame, text="Игнорировать папки:").pack(side=tk.LEFT)

        self.ignore_var = tk.StringVar(
            value="__pycache__, .git, node_modules, venv, .idea"
        )
        ttk.Entry(
            ignore_frame,
            textvariable=self.ignore_var,
            width=50
        ).pack(side=tk.LEFT, padx=5)

    def get_options(self) -> dict:
        return {
            'include_comments': self.comments_var.get(),
            'include_empty_lines': self.empty_var.get(),
            'include_structure': self.structure_var.get(),
            'ignore_dirs': [d.strip() for d in self.ignore_var.get().split(',')]
        }

    def set_options(self, options: dict):
        if 'include_comments' in options:
            self.comments_var.set(options['include_comments'])
        if 'include_empty_lines' in options:
            self.empty_var.set(options['include_empty_lines'])
        if 'include_structure' in options:
            self.structure_var.set(options['include_structure'])
        if 'ignore_dirs' in options:
            self.ignore_var.set(', '.join(options['ignore_dirs']))


class PreviewText(tk.Text):
    """Виджет предпросмотра кода"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, wrap=tk.WORD, font=('Consolas', 9), **kwargs)

        self.tag_configure('header', foreground='#2196F3', font=('Consolas', 9, 'bold'))
        self.tag_configure('file', foreground='#4CAF50', font=('Consolas', 9, 'italic'))
        self.tag_configure('error', foreground='#F44336')
        self.tag_configure('success', foreground='#4CAF50')

    def show_text(self, text: str, max_lines: int = 50):
        self.delete(1.0, tk.END)

        lines = text.split('\n')
        display_lines = lines[:max_lines]

        if len(lines) > max_lines:
            display_lines.append(f"\n\n... и еще {len(lines) - max_lines} строк")

        preview_text = '\n'.join(display_lines)
        self.insert(1.0, preview_text)

    def clear(self):
        self.delete(1.0, tk.END)
