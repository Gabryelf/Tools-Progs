import os
import sys
import subprocess
import shutil


def build_exe():
    print("=" * 50)
    print("  Сборка OverlayMarker.exe")
    print("=" * 50)
    print()

    # Проверяем наличие pyinstaller
    try:
        import PyInstaller
    except ImportError:
        print("Установка PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Очищаем старые сборки
    print("Очистка старых сборок...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)

    # Удаляем старые spec файлы
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            os.remove(file)

    print()
    print("Сборка exe...")

    # Команда для сборки
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name', 'OverlayMarker',
        '--console',
        '--add-data', 'src;src',
        '--hidden-import', 'PyQt5.QtCore',
        '--hidden-import', 'PyQt5.QtGui',
        '--hidden-import', 'PyQt5.QtWidgets',
        '--hidden-import', 'pynput',
        '--hidden-import', 'pynput.mouse',
        '--hidden-import', 'pynput.keyboard',
        '--hidden-import', 'src.core.drawing_engine',
        '--hidden-import', 'src.core.overlay_window',
        '--hidden-import', 'src.core.shape_manager',
        '--hidden-import', 'src.services.timer_service',
        '--hidden-import', 'src.services.input_blocker',
        '--hidden-import', 'src.ui.control_panel',
        '--hidden-import', 'src.ui.mini_panel',
        '--hidden-import', 'src.ui.styles',
        '--hidden-import', 'src.utils.constants',
        '--hidden-import', 'src.utils.helpers',
        'main.py'
    ]

    # Добавляем иконку если есть
    if os.path.exists('icon.ico'):
        cmd.insert(7, '--icon=icon.ico')

    # Запускаем сборку
    result = subprocess.run(cmd)

    print()
    if result.returncode == 0 and os.path.exists('dist/OverlayMarker.exe'):
        print("=" * 50)
        print("  ✅ Сборка успешно завершена!")
        print("  📁 Файл: dist/OverlayMarker.exe")
        print("=" * 50)
    else:
        print("=" * 50)
        print("  ❌ Ошибка при сборке!")
        print("=" * 50)


if __name__ == "__main__":
    build_exe()