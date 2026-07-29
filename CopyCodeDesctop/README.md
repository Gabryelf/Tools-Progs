
# 📋 Copy Code ++

> Универсальный копировщик кода проекта в буфер обмена с поддержкой множества языков программирования

Читая инструктаж к документации Pycharm искал удобную функцию для копирования всего кода проекта при создании промпта для ИИ, в итоге создал удобный инструмент для быстрого копирования кода из проектов. Решение - Python3 и его набор библиотек!

#### Возможности
- 📁 Выбор любой папки проекта для анализа
- 🔤 Поддержка 10+ языков программирования:
  - Python, JavaScript, TypeScript
  - HTML, CSS, SCSS
  - C, C++, Java
  - Go, Rust и другие
- ⚙️ Гибкие настройки:
  - Включение/выключение комментариев
  - Включение/выключение пустых строк
  - Показ структуры проекта
  - Настройка игнорируемых папок
- 📋 Копирование в буфер обмена
- 💾 Сохранение в файл (TXT, PY)
- 📤 Экспорт в ZIP архив
- 🎨 Поддержка SVG иконок
- 🔍 Предпросмотр кода перед копированием


#### Скриншоты

| Выбор проекта | Настройки | Сохранение |
|--------------|-------------|--------------|
| ![Main Window](https://github.com/Gabryelf/Tools-Progs/blob/main/docs/screens/copy_code/2026-07-29_21-47-33.png) | ![Language Select](https://github.com/Gabryelf/Tools-Progs/blob/main/docs/screens/copy_code/2026-07-29_21-50-56.png) | ![Preview](https://github.com/Gabryelf/Tools-Progs/blob/main/docs/screens/copy_code/2026-07-29_21-55-20.png) |

#### Технологии

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-0078D6?style=flat&logo=python&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-FF6C37?style=flat&logo=python&logoColor=white)
![PyInstaller](https://img.shields.io/badge/PyInstaller-FFD700?style=flat&logo=python&logoColor=white)

---

## 🔧 Использование

### Copy Code ++

1. **Запуск**: `python src/main.py`
2. **Выбор проекта**: Нажмите "Обзор..." и выберите папку с проектом
3. **Выбор языка**: Отметьте нужный язык программирования
4. **Настройка опций**: Включите/выключите комментарии, пустые строки, структуру
5. **Действия**:
   - 📋 **Копировать в буфер** - скопировать код в буфер обмена
   - 💾 **Сохранить в файл** - сохранить код в текстовый файл
   - 📤 **Экспорт в ZIP** - создать ZIP архив с кодом

#### Поддерживаемые языки

| Язык | Расширения |
|------|------------|
| Python | `.py`, `.pyw`, `.pyi` |
| JavaScript | `.js`, `.jsx`, `.ts`, `.tsx` |
| HTML | `.html`, `.htm`, `.xhtml` |
| CSS | `.css`, `.scss`, `.sass`, `.less` |
| C | `.c`, `.h` |
| C++ | `.cpp`, `.cc`, `.hpp`, `.hh` |
| Java | `.java`, `.kt`, `.kts` |
| Go | `.go` |
| Rust | `.rs` |

#### Горячие клавиши

| Комбинация | Действие |
|------------|----------|
| `Ctrl+C` | Копировать в буфер обмена |
| `Ctrl+S` | Сохранить в файл |
| `Ctrl+Z` | Экспорт в ZIP |
| `Ctrl+Q` | Выйти из приложения |

---

## 📁 Структура проекта

```
CopyCode/
├── src/                        # Исходный код
│   ├── main.py                 # Точка входа
│   ├── config.py               # Управление конфигурацией
│   ├── models/                 # Модели данных
│   │   ├── settings.py         # Настройки приложения
│   │   └── language.py         # Модель языка
│   ├── services/               # Сервисы
│   │   ├── code_collector.py   # Сбор кода
│   │   ├── file_processor.py   # Обработка файлов
│   │   └── clipboard_manager.py # Работа с буфером
│   ├── ui/                     # Интерфейс
│   │   ├── main_window.py      # Главное окно
│   │   ├── widgets.py          # Виджеты
│   │   ├── styles.py           # Стили
│   │   └── svg_renderer.py     # Рендеринг SVG
│   └── utils/                  # Утилиты
│       ├── helpers.py          # Вспомогательные функции
│       └── exceptions.py       # Исключения
├── assets/                     # Ресурсы
│   └── icons/                  # Иконки (SVG/PNG)
│       ├── app.ico             # Иконка приложения
│       ├── copy.svg            # Копировать
│       ├── save.svg            # Сохранить
│       ├── zip.svg             # ZIP архив
│       ├── folder.svg          # Папка
│       ├── comments.svg        # Комментарии
│       ├── empty.svg           # Пустые строки
│       ├── structure.svg       # Структура
│       ├── python.svg          # Python
│       ├── javascript.svg      # JavaScript
│       ├── html.svg            # HTML
│       ├── css.svg             # CSS
│       ├── c.svg               # C
│       ├── cpp.svg             # C++
│       ├── java.svg            # Java
│       ├── go.svg              # Go
│       └── rust.svg            # Rust
├── config/                     # Конфигурация
│   └── settings.json           # Настройки приложения
├── requirements.txt            # Зависимости
└── README.md                   # Документация
```

---

## 🛠️ Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/Gabryelf/Tools-Progs.git
cd Tools-Progs/СopyСode/src/
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Запуск приложения

```bash
python src/main.py
```

---

## 📦 Сборка EXE

### Windows

```bash
# Установка PyInstaller
pip install pyinstaller

# Сборка
pyinstaller --onefile --windowed --name "CopyCodePro" --icon assets/icons/app.ico src/main.py
```

### Сборка с дополнительными файлами

```bash
pyinstaller --onefile --windowed \
    --name "CopyCodePro" \
    --icon assets/icons/app.ico \
    --add-data "assets;assets" \
    --add-data "config;config" \
    --hidden-import pyperclip \
    src/main.py
```

---


## ✨ Возможности

- 📁 Выбор любой папки проекта
- 🔤 Поддержка множества языков: Python, JavaScript, HTML, CSS, C, C++, Java, Go, Rust и другие
- ⚙️ Гибкие настройки: включение/выключение комментариев, пустых строк, структуры проекта
- 📋 Копирование в буфер обмена
- 💾 Сохранение в файл
- 📤 Экспорт в ZIP архив
- 🎨 Удобный графический интерфейс



### Создание виртуального окружения
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Запуск приложения
```bash
python src/main.py
```

## 📁 Структура проекта

```
desctop_app/
├── assets/          # Ресурсы (иконки)
├── src/            # Исходный код
│   ├── models/     # Модели данных
│   ├── services/   # Сервисы
│   ├── ui/         # Интерфейс
│   └── utils/      # Вспомогательные функции
├── config/         # Конфигурация
├── tests/          # Тесты
└── README.md       # Документация
```

## ⚙️ Конфигурация

Файл `config/settings.json` позволяет настраивать:

- Языки программирования и их расширения
- Игнорируемые папки и файлы
- Параметры UI
- Пути к ресурсам

## 🙏 Благодарности

- [Tkinter](https://docs.python.org/3/library/tkinter.html) - за встроенный GUI
- [Pillow](https://python-pillow.org/) - за работу с изображениями
- [PyInstaller](https://pyinstaller.org/) - за сборку в EXE
- Всем контрибьюторам за помощь в развитии


<div align="center">
  <sub>Built with ❤️ in Python</sub>
</div>

---

<div align="center">
  <sub>07.2026 версия 0.0.3</sub>
</div>
```


