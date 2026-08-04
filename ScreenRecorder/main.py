# screen_recorder/main.py
"""
Точка входа в приложение
"""
import sys
import os
import logging
from pathlib import Path

# Добавляем путь к проекту
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

# Используем абсолютные импорты
from gui.main_window import MainWindow
from constants import APP_NAME, APP_VERSION, APP_AUTHOR, ICON_PATH


def setup_logging() -> None:
    """Настройка логирования"""
    log_dir = Path.home() / ".screen_recorder" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "screen_recorder.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def main() -> None:
    """Главная функция"""
    setup_logging()
    logger = logging.getLogger(__name__)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setApplicationDisplayName(APP_NAME)
    app.setOrganizationName(APP_AUTHOR)

    # Устанавливаем иконку приложения
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
        logger.info(f"Иконка загружена: {ICON_PATH}")
    else:
        logger.warning(f"Иконка не найдена: {ICON_PATH}")

    window = MainWindow()
    window.show()

    logger.info(f"Приложение {APP_NAME} v{APP_VERSION} запущено")

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
