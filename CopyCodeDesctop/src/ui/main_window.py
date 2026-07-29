"""
Главное окно приложения с поддержкой внешних файлов
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import threading
import os

from src.config import get_config
from src.models.settings import ApplicationSettings
from src.services.code_collector import CodeCollector
from src.services.clipboard_manager import ClipboardManager
from src.ui.widgets import (
    FileSelector, LanguageSelector, OptionsPanel,
    PreviewText, IconButton, IconLabel, IconManager,
    ExternalFilesList
)
from src.ui.styles import AppStyles


class MainWindow:
    """Главное окно приложения"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = get_config()
        self.settings = ApplicationSettings()

        # Папка с иконками
        self.icons_dir = self.config.icon_path

        # Сервисы
        self.code_collector = None
        self.clipboard_manager = ClipboardManager()

        # Переменные
        self.is_processing = False

        self._setup_window()
        self._create_widgets()
        self._bind_events()
        self._load_settings()

        self.update_status("✅ Готов к работе")

    def _setup_window(self):
        """Настройка окна"""
        self.root.title(f"{self.config.get('app.name', 'Copy Code Pro')}")

        width = self.settings.window_width
        height = self.settings.window_height
        self.root.geometry(f"{width}x{700}")
        self.root.minsize(700, 600)

        # Иконка окна
        icon_path = self.icons_dir / "app.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except:
                pass

        AppStyles.setup_styles()
        self.colors = AppStyles.get_colors()

    def _create_widgets(self):
        """Создание виджетов с иконками"""
        # Основной контейнер с прокруткой
        self.main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(
            self.root,
            orient="vertical",
            command=self.main_canvas.yview
        )

        self.scrollable_frame = ttk.Frame(self.main_canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---- Заголовок ----
        self._create_header()

        # ---- Выбор проекта ----
        self._create_project_selector()

        # ---- Выбор языка ----
        self._create_language_selector()

        # ---- Внешние файлы (НОВОЕ) ----
        self._create_external_files_section()

        # ---- Опции ----
        self._create_options_panel()

        # ---- Кнопки действий ----
        self._create_action_buttons()

        # ---- Прогресс ----
        self._create_progress()

        # ---- Статус ----
        self._create_status()

        # ---- Предпросмотр ----
        self._create_preview()

        # Веса для растягивания
        self.scrollable_frame.columnconfigure(1, weight=1)
        self.scrollable_frame.rowconfigure(10, weight=1)

    def _create_header(self):
        """Создание заголовка с логотипом"""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=15)

        logo_path = self.icons_dir / "logo.svg"
        if logo_path.exists():
            logo_label = IconLabel(
                header_frame,
                icon_path=logo_path,
                icon_size=(48, 48)
            )
            logo_label.pack(side=tk.LEFT, padx=10)

        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)

        ttk.Label(
            title_frame,
            text="Copy Code Pro",
            style='Title.TLabel'
        ).pack(anchor=tk.W)

        ttk.Label(
            title_frame,
            text="Универсальный копировщик кода с поддержкой внешних файлов",
            style='Subtitle.TLabel'
        ).pack(anchor=tk.W)

    def _create_project_selector(self):
        """Создание выбора проекта"""
        folder_icon = self.icons_dir / "folder.svg"

        self.project_selector = FileSelector(
            self.scrollable_frame,
            label="Проект:",
            on_select=self._on_project_selected,
            icon_path=folder_icon if folder_icon.exists() else None
        )
        self.project_selector.grid(
            row=1, column=0, columnspan=3,
            sticky=tk.W + tk.E, padx=10, pady=5
        )

    def _create_language_selector(self):
        """Создание выбора языка"""
        languages = ['all', 'python', 'javascript', 'html', 'css', 'c', 'cpp', 'java', 'go', 'rust']

        self.language_selector = LanguageSelector(
            self.scrollable_frame,
            languages=languages,
            on_select=self._on_language_selected,
            icons_dir=self.icons_dir
        )
        self.language_selector.grid(
            row=2, column=0, columnspan=3,
            sticky=tk.W + tk.E, padx=10, pady=10
        )

    def _create_external_files_section(self):
        """Создание секции внешних файлов (НОВАЯ)"""
        external_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="📎 Внешние файлы",
            padding="5"
        )
        external_frame.grid(
            row=3, column=0, columnspan=3,
            sticky=tk.W + tk.E, padx=10, pady=5
        )

        # Кнопка добавления файлов
        add_frame = ttk.Frame(external_frame)
        add_frame.pack(fill=tk.X, pady=5)

        add_icon = self.icons_dir / "add_file.svg"
        if add_icon.exists():
            add_btn = IconButton(
                add_frame,
                icon_path=add_icon,
                text="Добавить файл",
                command=self._add_external_file,
                icon_size=(16, 16)
            )
            add_btn.pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(
                add_frame,
                text="➕ Добавить файл",
                command=self._add_external_file
            ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            add_frame,
            text="🗑 Очистить все",
            command=self._clear_external_files
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(
            add_frame,
            text="Добавьте файлы из любого места для включения в сборку",
            foreground='gray'
        ).pack(side=tk.LEFT, padx=20)

        # Список внешних файлов
        self.external_files_list = ExternalFilesList(
            external_frame,
            on_remove=self._remove_external_file
        )
        self.external_files_list.pack(fill=tk.BOTH, expand=True, pady=5)

    def _create_options_panel(self):
        """Создание панели опций"""
        self.options_panel = OptionsPanel(
            self.scrollable_frame,
            icons_dir=self.icons_dir
        )
        self.options_panel.grid(
            row=4, column=0, columnspan=3,
            sticky=tk.W + tk.E, padx=10, pady=10
        )

    def _create_action_buttons(self):
        """Создание кнопок действий"""
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=15)

        # Иконки для кнопок
        copy_icon = self.icons_dir / "copy.svg"
        save_icon = self.icons_dir / "save.svg"
        zip_icon = self.icons_dir / "zip.svg"

        # Кнопка копирования
        if copy_icon.exists():
            copy_btn = IconButton(
                button_frame,
                icon_path=copy_icon,
                text="Копировать в буфер",
                command=self._copy_to_clipboard,
                icon_size=(20, 20),
                style='Action.TButton',
                width=22
            )
        else:
            copy_btn = ttk.Button(
                button_frame,
                text="📋 Копировать в буфер",
                command=self._copy_to_clipboard,
                style='Action.TButton',
                width=22
            )
        copy_btn.grid(row=0, column=0, padx=5)

        # Кнопка сохранения
        if save_icon.exists():
            save_btn = IconButton(
                button_frame,
                icon_path=save_icon,
                text="Сохранить в файл",
                command=self._save_to_file,
                icon_size=(20, 20),
                style='Action.TButton',
                width=22
            )
        else:
            save_btn = ttk.Button(
                button_frame,
                text="💾 Сохранить в файл",
                command=self._save_to_file,
                style='Action.TButton',
                width=22
            )
        save_btn.grid(row=0, column=1, padx=5)

        # Кнопка ZIP
        if zip_icon.exists():
            zip_btn = IconButton(
                button_frame,
                icon_path=zip_icon,
                text="Экспорт в ZIP",
                command=self._export_zip,
                icon_size=(20, 20),
                style='Action.TButton',
                width=22
            )
        else:
            zip_btn = ttk.Button(
                button_frame,
                text="📤 Экспорт в ZIP",
                command=self._export_zip,
                style='Action.TButton',
                width=22
            )
        zip_btn.grid(row=0, column=2, padx=5)

    def _create_progress(self):
        """Создание прогресс-бара"""
        self.progress = ttk.Progressbar(
            self.scrollable_frame,
            mode='indeterminate',
            length=600,
            style='Progress.Horizontal.TProgressbar'
        )
        self.progress.grid(row=6, column=0, columnspan=3, pady=10, padx=10)

    def _create_status(self):
        """Создание статуса"""
        self.status_label = ttk.Label(
            self.scrollable_frame,
            text="Готов",
            style='Status.TLabel'
        )
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)

    def _create_preview(self):
        """Создание предпросмотра"""
        preview_label_frame = ttk.Frame(self.scrollable_frame)
        preview_label_frame.grid(row=8, column=0, columnspan=3, sticky=tk.W, pady=5, padx=10)

        code_icon = self.icons_dir / "code.svg"
        if code_icon.exists():
            icon_label = IconLabel(
                preview_label_frame,
                icon_path=code_icon,
                icon_size=(16, 16),
                text="Предпросмотр:"
            )
            icon_label.pack(side=tk.LEFT)
        else:
            ttk.Label(preview_label_frame, text="📄 Предпросмотр:").pack(side=tk.LEFT)

        text_frame = ttk.Frame(self.scrollable_frame)
        text_frame.grid(row=9, column=0, columnspan=3, sticky=tk.W + tk.E + tk.N + tk.S, padx=10)

        self.preview_text = PreviewText(text_frame, height=12)
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        preview_scrollbar = ttk.Scrollbar(
            text_frame,
            orient=tk.VERTICAL,
            command=self.preview_text.yview
        )
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text['yscrollcommand'] = preview_scrollbar.set

    def _bind_events(self):
        """Привязка событий"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _load_settings(self):
        """Загрузка настроек"""
        if self.settings.project_path.exists():
            self.project_selector.set_path(self.settings.project_path)

        self.language_selector.set_language(self.settings.language)

        self.options_panel.set_options({
            'include_comments': self.settings.include_comments,
            'include_empty_lines': self.settings.include_empty_lines,
            'include_structure': self.settings.include_structure,
            'ignore_dirs': self.settings.ignore_dirs
        })

    def _on_project_selected(self, path: Path):
        self.settings.project_path = path
        self.settings.save()
        self.update_status(f"📁 Выбран проект: {path.name}")

    def _on_language_selected(self, language: str):
        self.settings.language = language
        self.settings.save()

    def _add_external_file(self):
        """Добавление внешнего файла"""
        file_paths = filedialog.askopenfilenames(
            title="Выберите файлы для добавления",
            filetypes=[
                ("All files", "*.*"),
                ("Python files", "*.py"),
                ("Text files", "*.txt"),
                ("JavaScript files", "*.js"),
                ("HTML files", "*.html"),
                ("CSS files", "*.css"),
                ("C++ files", "*.cpp"),
                ("Java files", "*.java")
            ]
        )

        if not file_paths:
            return

        # Создаем code_collector если его нет
        if not self.code_collector:
            options = self.options_panel.get_options()
            self.settings.include_comments = options['include_comments']
            self.settings.include_empty_lines = options['include_empty_lines']
            self.settings.include_structure = options['include_structure']
            self.settings.ignore_dirs = options['ignore_dirs']
            self.code_collector = CodeCollector(self.settings)

        added = 0
        for file_path in file_paths:
            if self.code_collector.add_external_file(Path(file_path)):
                added += 1

        # Обновляем список
        self._update_external_files_list()
        self.update_status(f"✅ Добавлено {added} внешних файлов")

    def _remove_external_file(self, index: int):
        """Удаление внешнего файла"""
        if self.code_collector:
            if self.code_collector.remove_external_file(index):
                self._update_external_files_list()
                self.update_status(f"🗑 Файл удален")

    def _clear_external_files(self):
        """Очистка внешних файлов"""
        if self.code_collector and self.code_collector.get_external_files_count() > 0:
            if messagebox.askyesno("Подтверждение", "Удалить все внешние файлы?"):
                self.code_collector.clear_external_files()
                self._update_external_files_list()
                self.update_status("🗑 Все внешние файлы удалены")

    def _update_external_files_list(self):
        """Обновление списка внешних файлов"""
        if self.code_collector:
            files = self.code_collector.get_external_files()
            self.external_files_list.update_files(files)

    def _collect_code(self) -> str:
        """Сбор кода"""
        options = self.options_panel.get_options()
        self.settings.include_comments = options['include_comments']
        self.settings.include_empty_lines = options['include_empty_lines']
        self.settings.include_structure = options['include_structure']
        self.settings.ignore_dirs = options['ignore_dirs']

        self.code_collector = CodeCollector(self.settings)

        # Добавляем внешние файлы если они уже были
        # (они сохраняются в отдельном файле настроек)

        return self.code_collector.collect(
            include_external=options.get('include_external', True)
        )

    def _copy_to_clipboard(self):
        """Копирование в буфер обмена"""
        if self.is_processing:
            return

        def copy_thread():
            self.is_processing = True
            self._start_progress()

            try:
                code = self._collect_code()

                if code and not code.startswith('❌'):
                    success = self.clipboard_manager.copy_to_clipboard(code)

                    if success:
                        files_count = self.code_collector.get_files_count()
                        external_count = self.code_collector.get_external_files_count()
                        status_msg = f"✅ Скопировано! ({files_count} файлов проекта"
                        if external_count > 0:
                            status_msg += f", {external_count} внешних"
                        status_msg += ")"
                        self.update_status(status_msg)

                        self.root.after(0, lambda: self.preview_text.show_text(code))

                        self.root.after(0, lambda: messagebox.showinfo(
                            "Успех",
                            f"✅ Код скопирован в буфер обмена!\n"
                            f"📊 Файлов проекта: {files_count}\n"
                            f"📎 Внешних файлов: {external_count}"
                        ))
                    else:
                        self.update_status("❌ Ошибка копирования")
                        self.root.after(0, lambda: messagebox.showerror(
                            "Ошибка",
                            "Не удалось скопировать в буфер обмена"
                        ))
                else:
                    self.update_status("❌ Ошибка сбора кода")
                    self.root.after(0, lambda: messagebox.showerror(
                        "Ошибка",
                        code or "Не удалось собрать код"
                    ))

            except Exception as e:
                self.update_status(f"❌ Ошибка: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка",
                    f"Произошла ошибка:\n{str(e)}"
                ))
            finally:
                self.is_processing = False
                self._stop_progress()

        threading.Thread(target=copy_thread, daemon=True).start()

    def _save_to_file(self):
        """Сохранение в файл"""
        if self.is_processing:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        def save_thread():
            self.is_processing = True
            self._start_progress()

            try:
                code = self._collect_code()
                if code and not code.startswith('❌'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(code)

                    files_count = self.code_collector.get_files_count()
                    external_count = self.code_collector.get_external_files_count()
                    status_msg = f"✅ Сохранено! ({files_count} файлов проекта"
                    if external_count > 0:
                        status_msg += f", {external_count} внешних"
                    status_msg += ")"
                    self.update_status(status_msg)

                    self.root.after(0, lambda: messagebox.showinfo(
                        "Успех",
                        f"✅ Код сохранен в:\n{file_path}\n"
                        f"📊 Файлов проекта: {files_count}\n"
                        f"📎 Внешних файлов: {external_count}"
                    ))
                else:
                    self.update_status("❌ Ошибка сбора кода")
                    self.root.after(0, lambda: messagebox.showerror(
                        "Ошибка",
                        code or "Не удалось собрать код"
                    ))

            except Exception as e:
                self.update_status(f"❌ Ошибка: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка",
                    f"Не удалось сохранить:\n{str(e)}"
                ))
            finally:
                self.is_processing = False
                self._stop_progress()

        threading.Thread(target=save_thread, daemon=True).start()

    def _export_zip(self):
        """Экспорт в ZIP"""
        if self.is_processing:
            return

        try:
            import zipfile
        except ImportError:
            messagebox.showerror("Ошибка", "Модуль zipfile не найден")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("ZIP archive", "*.zip")]
        )

        if not file_path:
            return

        def zip_thread():
            self.is_processing = True
            self._start_progress()

            try:
                options = self.options_panel.get_options()
                ignore_dirs = options['ignore_dirs']
                language = self.language_selector.get_language()

                from src.models.language import get_language_registry
                registry = get_language_registry()

                if language == 'all':
                    extensions = registry.get_all_extensions()
                else:
                    lang_obj = registry.get_language(language)
                    extensions = lang_obj.get_extensions() if lang_obj else set()

                count = 0
                project_path = self.settings.project_path

                with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(project_path):
                        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]

                        for file in files:
                            file_path_full = Path(root) / file
                            if file_path_full.suffix in extensions:
                                arcname = file_path_full.relative_to(project_path)
                                zipf.write(file_path_full, arcname)
                                count += 1

                    # Добавляем внешние файлы если они есть
                    if self.code_collector:
                        external_files = self.code_collector.get_external_files()
                        for ext_file in external_files:
                            ext_path = Path(ext_file['path'])
                            if ext_path.exists():
                                arcname = f"external/{ext_path.name}"
                                zipf.write(ext_path, arcname)
                                count += 1

                self.update_status(f"✅ ZIP создан: {Path(file_path).name} ({count} файлов)")

                self.root.after(0, lambda: messagebox.showinfo(
                    "Успех",
                    f"✅ ZIP архив создан:\n{file_path}\n"
                    f"📊 Файлов: {count}"
                ))

            except Exception as e:
                self.update_status(f"❌ Ошибка: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка",
                    f"Не удалось создать ZIP:\n{str(e)}"
                ))
            finally:
                self.is_processing = False
                self._stop_progress()

        threading.Thread(target=zip_thread, daemon=True).start()

    def _start_progress(self):
        self.root.after(0, self.progress.start)

    def _stop_progress(self):
        self.root.after(0, self.progress.stop)

    def update_status(self, message: str):
        self.root.after(0, lambda: self.status_label.config(text=message))

    def _on_closing(self):
        self.settings.save()
        IconManager.clear_cache()
        self.root.destroy()
