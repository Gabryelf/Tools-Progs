"""
copy_code_gui.py - Десктопное приложение для копирования кода
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import pyperclip
import json
from typing import Set, List
import os


class CodeCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📋 Copy Code Pro")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Настройки
        self.settings_file = Path.home() / ".copycode_settings.json"
        self.project_path = Path.cwd()
        self.settings = self.load_settings()

        self.setup_ui()
        self.update_status("Готов к работе")

    def setup_ui(self):
        """Создание интерфейса"""
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Заголовок
        title = ttk.Label(
            main_frame,
            text="🚀 Copy Code Pro",
            font=('Arial', 16, 'bold')
        )
        title.grid(row=0, column=0, columnspan=3, pady=10)

        # Выбор проекта
        ttk.Label(main_frame, text="📁 Проект:").grid(row=1, column=0, sticky=tk.W)
        self.project_var = tk.StringVar(value=str(self.project_path))
        project_entry = ttk.Entry(main_frame, textvariable=self.project_var, width=50)
        project_entry.grid(row=1, column=1, padx=5)
        ttk.Button(
            main_frame,
            text="Обзор",
            command=self.select_project
        ).grid(row=1, column=2)

        # Выбор языка
        ttk.Label(main_frame, text="🔤 Язык:").grid(row=2, column=0, sticky=tk.W, pady=10)

        self.language_frame = ttk.Frame(main_frame)
        self.language_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W)

        self.language_var = tk.StringVar(value="all")
        languages = [
            ("Все языки", "all"),
            ("Python", "python"),
            ("JavaScript", "javascript"),
            ("HTML", "html"),
            ("CSS", "css"),
            ("C", "c"),
            ("C++", "cpp"),
            ("Java", "java"),
            ("Go", "go"),
            ("Rust", "rust")
        ]

        for i, (text, value) in enumerate(languages):
            row = i // 4
            col = i % 4
            ttk.Radiobutton(
                self.language_frame,
                text=text,
                value=value,
                variable=self.language_var
            ).grid(row=row, column=col, sticky=tk.W, padx=10)

        # Настройки
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Настройки", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.include_comments = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Включать комментарии",
            variable=self.include_comments
        ).grid(row=0, column=0, sticky=tk.W)

        self.include_empty = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Включать пустые строки",
            variable=self.include_empty
        ).grid(row=0, column=1, sticky=tk.W, padx=20)

        self.include_structure = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Показывать структуру проекта",
            variable=self.include_structure
        ).grid(row=0, column=2, sticky=tk.W, padx=20)

        # Игнорируемые папки
        ttk.Label(options_frame, text="Игнорировать папки:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ignore_var = tk.StringVar(
            value="__pycache__, .git, node_modules, venv, .idea"
        )
        ignore_entry = ttk.Entry(options_frame, textvariable=self.ignore_var, width=50)
        ignore_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5)

        # Кнопки действий
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, columnspan=3, pady=20)

        ttk.Button(
            action_frame,
            text="📋 Копировать в буфер",
            command=self.copy_to_clipboard,
            width=20
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            action_frame,
            text="💾 Сохранить в файл",
            command=self.save_to_file,
            width=20
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            action_frame,
            text="📤 Экспорт в ZIP",
            command=self.export_zip,
            width=20
        ).grid(row=0, column=2, padx=5)

        # Прогресс-бар
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=580
        )
        self.progress.grid(row=5, column=0, columnspan=3, pady=10)

        # Статус
        self.status_label = ttk.Label(main_frame, text="Готов")
        self.status_label.grid(row=6, column=0, columnspan=3)

        # Текстовое поле для предпросмотра
        ttk.Label(main_frame, text="📄 Предпросмотр:").grid(row=7, column=0, sticky=tk.W, pady=5)

        self.preview_text = tk.Text(main_frame, height=8, wrap=tk.NONE)
        self.preview_text.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        scrollbar.grid(row=8, column=3, sticky=(tk.N, tk.S))
        self.preview_text['yscrollcommand'] = scrollbar.set

    def load_settings(self) -> dict:
        """Загрузка настроек"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'ignore_dirs': ['__pycache__', '.git', 'node_modules', 'venv', '.idea']
        }

    def save_settings(self):
        """Сохранение настроек"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except:
            pass

    def select_project(self):
        """Выбор папки проекта"""
        folder = filedialog.askdirectory()
        if folder:
            self.project_path = Path(folder)
            self.project_var.set(str(self.project_path))
            self.update_status(f"Выбран проект: {self.project_path.name}")

    def collect_code(self) -> str:
        """Сборка кода проекта"""
        self.progress.start()
        self.update_status("Сборка кода...")

        try:
            extensions = self.get_extensions(self.language_var.get())
            ignore_dirs = [d.strip() for d in self.ignore_var.get().split(',')]

            result = []
            files_count = 0

            if self.include_structure.get():
                result.append("📁 СТРУКТУРА ПРОЕКТА")
                result.append("=" * 80)

                for root, dirs, files in os.walk(self.project_path):
                    dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
                    level = root.replace(str(self.project_path), '').count(os.sep)
                    indent = '  ' * level
                    result.append(f"{indent}📁 {Path(root).name}/")

                    for file in sorted(files):
                        if Path(file).suffix in extensions:
                            result.append(f"{indent}  📄 {file}")
                            files_count += 1

                result.append("")
                result.append("=" * 80)
                result.append("")

            # Собираем содержимое файлов
            for root, dirs, files in os.walk(self.project_path):
                dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]

                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix in extensions:
                        relative_path = file_path.relative_to(self.project_path)
                        result.append("")
                        result.append("-" * 80)
                        result.append(f"📄 {relative_path}")
                        result.append("-" * 80)

                        content = self.process_file(file_path)
                        if content:
                            result.extend(content)

                        files_count += 1

            self.progress.stop()
            self.update_status(f"✅ Обработано {files_count} файлов")
            return '\n'.join(result)

        except Exception as e:
            self.progress.stop()
            self.update_status(f"❌ Ошибка: {str(e)}")
            return f"Ошибка: {str(e)}"

    def process_file(self, file_path: Path) -> List[str]:
        """Обработка файла"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            processed = []
            in_multiline = False

            for line in lines:
                # Пропускаем пустые строки
                if not self.include_empty.get() and not line.strip():
                    continue

                # Обработка многострочных комментариев Python
                if "'''" in line or '"""' in line:
                    in_multiline = not in_multiline
                    if not self.include_comments.get():
                        continue

                if not self.include_comments.get() and in_multiline:
                    continue

                if self.include_comments.get():
                    processed.append(line.rstrip())
                else:
                    # Удаляем однострочные комментарии
                    clean_line = line.rstrip()
                    for comment in ['#', '//']:
                        if comment in clean_line:
                            clean_line = clean_line.split(comment)[0].rstrip()
                    if clean_line or self.include_empty.get():
                        processed.append(clean_line)

            return processed
        except:
            return []

    def get_extensions(self, language: str) -> Set[str]:
        """Получение расширений для языка"""
        extensions = {
            'python': {'.py', '.pyw', '.pyi'},
            'javascript': {'.js', '.jsx', '.mjs', '.ts', '.tsx'},
            'html': {'.html', '.htm', '.xhtml'},
            'css': {'.css', '.scss', '.sass', '.less'},
            'c': {'.c', '.h'},
            'cpp': {'.cpp', '.cc', '.cxx', '.hpp', '.hh', '.hxx'},
            'java': {'.java', '.kt', '.kts'},
            'go': {'.go'},
            'rust': {'.rs'},
            'all': set()
        }

        if language == 'all':
            all_ext = set()
            for exts in extensions.values():
                all_ext.update(exts)
            return all_ext

        return extensions.get(language, set())

    def copy_to_clipboard(self):
        """Копирование в буфер обмена"""

        def copy_thread():
            code = self.collect_code()
            if code:
                pyperclip.copy(code)
                self.update_status("✅ Скопировано в буфер обмена!")
                messagebox.showinfo("Успех", "Код скопирован в буфер обмена!")

                # Обновляем предпросмотр
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, code[:2000] + "\n... (показано начало)")

        threading.Thread(target=copy_thread, daemon=True).start()

    def save_to_file(self):
        """Сохранение в файл"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            def save_thread():
                code = self.collect_code()
                if code:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(code)
                    self.update_status(f"✅ Сохранено в {Path(file_path).name}")
                    messagebox.showinfo("Успех", f"Код сохранен в {file_path}")

            threading.Thread(target=save_thread, daemon=True).start()

    def export_zip(self):
        """Экспорт в ZIP архив"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("ZIP archive", "*.zip")]
        )
        if file_path:
            import zipfile

            def zip_thread():
                ignore_dirs = [d.strip() for d in self.ignore_var.get().split(',')]
                extensions = self.get_extensions(self.language_var.get())

                with zipfile.ZipFile(file_path, 'w') as zipf:
                    for root, dirs, files in os.walk(self.project_path):
                        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]

                        for file in files:
                            file_path_full = Path(root) / file
                            if file_path_full.suffix in extensions:
                                arcname = file_path_full.relative_to(self.project_path)
                                zipf.write(file_path_full, arcname)

                self.update_status(f"✅ ZIP создан: {Path(file_path).name}")
                messagebox.showinfo("Успех", f"ZIP архив создан: {file_path}")

            threading.Thread(target=zip_thread, daemon=True).start()

    def update_status(self, message: str):
        """Обновление статуса"""
        self.status_label.config(text=message)


def main():
    root = tk.Tk()
    app = CodeCopyApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
    