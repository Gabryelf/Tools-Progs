"""
Скрипт для сборки EXE файла с отладкой
Запускайте: python build.py
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build():
    """Очистка старых сборок"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ Очищена папка: {dir_name}")


def check_dependencies():
    """Проверка установленных зависимостей"""
    print("\n📦 Проверка зависимостей:")
    deps = [
        'PyQt5', 'cv2', 'numpy', 'sounddevice', 'soundfile',
        'pyautogui', 'moviepy', 'scipy', 'PIL'
    ]
    missing = []
    for dep in deps:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - НЕ УСТАНОВЛЕН")
            missing.append(dep)

    if missing:
        print(f"\n⚠️ Отсутствуют зависимости: {', '.join(missing)}")
        print("Установите их командой:")
        print(f"pip install {' '.join(missing)}")
        return False
    return True


def build_exe():
    """Сборка EXE файла с подробным выводом"""
    print("\n🚀 Начинаю сборку EXE...")

    # Сначала попробуем собрать без --windowed для отладки
    print("\n🔧 Шаг 1: Сборка без --windowed (для отладки)...")

    cmd_debug = [
        'pyinstaller',
        '--onefile',
        '--name', 'ScreenRecorder_debug',
        '--add-data', 'assets;assets',
        '--add-data', 'config;config',
        '--icon', 'assets/icon.ico',
        '--hidden-import', 'PyQt5',
        '--hidden-import', 'PyQt5.QtCore',
        '--hidden-import', 'PyQt5.QtGui',
        '--hidden-import', 'PyQt5.QtWidgets',
        '--hidden-import', 'cv2',
        '--hidden-import', 'numpy',
        '--hidden-import', 'sounddevice',
        '--hidden-import', 'soundfile',
        '--hidden-import', 'pyautogui',
        '--hidden-import', 'moviepy',
        '--hidden-import', 'moviepy.editor',
        '--hidden-import', 'scipy',
        '--hidden-import', 'scipy.signal',
        '--hidden-import', 'PIL',
        '--hidden-import', 'core',
        '--hidden-import', 'gui',
        '--hidden-import', 'utils',
        '--hidden-import', 'constants',
        '__main__.py'
    ]

    try:
        # Запускаем с захватом вывода
        result = subprocess.run(
            cmd_debug,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        # Выводим stdout
        if result.stdout:
            print("\n📄 STDOUT:")
            print(result.stdout)

        # Выводим stderr
        if result.stderr:
            print("\n⚠️ STDERR:")
            print(result.stderr)

        # Проверяем результат
        if result.returncode != 0:
            print(f"\n❌ Ошибка сборки (код: {result.returncode})")

            # Ищем конкретную ошибку
            if "No module named" in result.stderr:
                import re
                match = re.search(r"No module named '([^']+)'", result.stderr)
                if match:
                    print(f"\n🔍 Не найден модуль: {match.group(1)}")
                    print(f"   Попробуйте установить: pip install {match.group(1)}")

            return False

        print("\n✅ Отладочная сборка успешна!")
        print("🔧 Шаг 2: Сборка с --windowed...")

        # Теперь собираем финальную версию с --windowed
        cmd_final = cmd_debug.copy()
        cmd_final[cmd_final.index('--name') + 1] = 'ScreenRecorder'
        cmd_final.insert(cmd_final.index('--onefile') + 1, '--windowed')

        result2 = subprocess.run(
            cmd_final,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        if result2.stdout:
            print(result2.stdout)
        if result2.stderr:
            print(result2.stderr)

        if result2.returncode != 0:
            print(f"\n❌ Ошибка финальной сборки (код: {result2.returncode})")
            return False

        print("\n✅ Сборка завершена успешно!")
        exe_path = os.path.abspath('dist/ScreenRecorder.exe')
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 EXE файл: {exe_path}")
            print(f"📏 Размер: {size:.2f} MB")

        # Удаляем отладочную версию
        debug_exe = os.path.abspath('dist/ScreenRecorder_debug.exe')
        if os.path.exists(debug_exe):
            os.remove(debug_exe)
            print("🧹 Удален отладочный EXE")

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка выполнения: {e}")
        return False


def create_spec_file():
    """Создание .spec файла"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config', 'config'),
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'cv2',
        'numpy',
        'sounddevice',
        'soundfile',
        'pyautogui',
        'moviepy',
        'moviepy.editor',
        'scipy',
        'scipy.signal',
        'PIL',
        'core',
        'core.settings',
        'core.recorder',
        'core.audio_processor',
        'gui',
        'gui.main_window',
        'gui.drawing_toolbar',
        'gui.modern_styles',
        'gui.styles',
        'utils',
        'utils.helpers',
        'constants',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyd = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyd,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ScreenRecorder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
'''
    with open('ScreenRecorder.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ Создан файл ScreenRecorder.spec")


def check_pyinstaller():
    """Проверка установки PyInstaller"""
    try:
        result = subprocess.run(
            ['pyinstaller', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ PyInstaller версия: {result.stdout.strip()}")
            return True
        else:
            print("❌ PyInstaller не работает")
            return False
    except FileNotFoundError:
        print("❌ PyInstaller не установлен")
        print("   Установите: pip install pyinstaller")
        return False


def main():
    """Главная функция"""
    print("=" * 60)
    print("🔧 СБОРКА SCREEN RECORDER")
    print("=" * 60)

    # Проверяем версию Python
    print(f"\n🐍 Python версия: {sys.version}")

    # Проверяем PyInstaller
    if not check_pyinstaller():
        sys.exit(1)

    # Проверяем зависимости
    if not check_dependencies():
        print("\n❌ Установите недостающие зависимости и повторите сборку.")
        sys.exit(1)

    # Проверяем наличие иконки
    if not os.path.exists('assets/icon.ico'):
        print("\n⚠️ Иконка не найдена, создаю...")
        try:
            from create_icon import create_app_icon
            create_app_icon()
        except Exception as e:
            print(f"❌ Ошибка создания иконки: {e}")
            sys.exit(1)

    # Создаем .spec файл
    create_spec_file()

    # Очистка старых сборок
    clean_build()

    # Сборка
    success = build_exe()

    if success:
        print("\n" + "=" * 60)
        print("✅ СБОРКА ЗАВЕРШЕНА")
        print("=" * 60)
        print("\n💡 Файл находится в папке dist/")
        print("   Запустите ScreenRecorder.exe для проверки")
    else:
        print("\n" + "=" * 60)
        print("❌ СБОРКА НЕ УДАЛАСЬ")
        print("=" * 60)
        print("\n💡 Попробуйте:")
        print("   1. Запустите сборку вручную:")
        print("      pyinstaller --onefile --name ScreenRecorder_debug --add-data assets;assets --add-data config;config __main__.py")
        print("   2. Проверьте файл warn-ScreenRecorder_debug.txt в папке build")
        print("   3. Проверьте файл ScreenRecorder_debug.exe в папке dist")
        sys.exit(1)


if __name__ == '__main__':
    main()