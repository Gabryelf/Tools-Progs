"""
Скрипт для сборки EXE файла
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


def build_exe():
    """Сборка EXE файла"""
    print("🚀 Начинаю сборку EXE...")

    # Команда для сборки
    cmd = [
        'pyinstaller',
        '--onefile',  # Один файл
        '--windowed',  # Без консоли
        '--name', 'ScreenRecorder',
        '--add-data', 'assets;assets',
        '--add-data', 'config;config',
        '--icon', 'assets/icon.ico',
        '--hidden-import=gui',
        '--hidden-import=gui.main_window',
        '--hidden-import=gui.drawing_toolbar',
        '--hidden-import=gui.modern_styles',
        '--hidden-import=gui.styles',
        '--hidden-import=core',
        '--hidden-import=core.settings',
        '--hidden-import=core.recorder',
        '--hidden-import=core.audio_processor',
        '--hidden-import=utils',
        '--hidden-import=utils.helpers',
        '--hidden-import=constants',
        '--hidden-import=sounddevice',
        '--hidden-import=soundfile',
        '--hidden-import=pyautogui',
        '--hidden-import=moviepy',
        '--hidden-import=moviepy.editor',
        '--hidden-import=scipy',
        '--hidden-import=scipy.signal',
        '--hidden-import=numpy',
        '--hidden-import=cv2',
        '--hidden-import=PIL',
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--collect-all', 'gui',
        '--collect-all', 'core',
        '--collect-all', 'utils',
        '__main__.py'
    ]

    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Сборка завершена успешно!")
        print(f"📁 EXE файл: {os.path.abspath('dist/ScreenRecorder.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка сборки: {e}")
        sys.exit(1)


def main():
    """Главная функция"""
    print("=" * 60)
    print("🔧 СБОРКА SCREEN RECORDER")
    print("=" * 60)

    # Проверяем наличие иконки
    if not os.path.exists('assets/icon.ico'):
        print("⚠️ Иконка не найдена, создаю...")
        from create_icon import create_app_icon
        create_app_icon()

    clean_build()
    build_exe()

    print("\n" + "=" * 60)
    print("✅ СБОРКА ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == '__main__':
    main()
