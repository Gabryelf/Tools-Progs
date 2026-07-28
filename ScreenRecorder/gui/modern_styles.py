"""
Современные стили для интерфейса (темная тема)
"""

DARK_STYLE = """
    /* Основные цвета */
    QWidget {
        background-color: #1e1e1e;
        color: #d4d4d4;
        font-family: 'Segoe UI', 'Microsoft Sans Serif', sans-serif;
        font-size: 13px;
    }

    /* Главное окно */
    QMainWindow {
        background-color: #1e1e1e;
        border: 1px solid #3c3c3c;
    }

    /* Заголовок */
    QLabel#titleLabel {
        color: #ffffff;
        font-size: 22px;
        font-weight: bold;
        padding: 10px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #2d2d2d, stop:1 #1e1e1e);
        border-bottom: 2px solid #007acc;
    }

    /* Вкладки */
    QTabWidget::pane {
        background-color: #252526;
        border: 1px solid #3c3c3c;
        border-radius: 4px;
        padding: 5px;
    }

    QTabBar::tab {
        background-color: #2d2d2d;
        color: #999999;
        padding: 8px 16px;
        margin: 2px;
        border: 1px solid #3c3c3c;
        border-radius: 4px;
        font-weight: bold;
    }

    QTabBar::tab:selected {
        background-color: #3c3c3c;
        color: #ffffff;
        border-color: #007acc;
    }

    QTabBar::tab:hover:!selected {
        background-color: #3a3a3a;
        color: #d4d4d4;
    }

    /* Группы */
    QGroupBox {
        background-color: #2d2d2d;
        border: 1px solid #3c3c3c;
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 12px;
        font-weight: bold;
        color: #d4d4d4;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px;
        color: #007acc;
    }

    /* Кнопки */
    QPushButton {
        background-color: #3c3c3c;
        color: #d4d4d4;
        border: none;
        padding: 10px 18px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
        min-height: 20px;
    }

    QPushButton:hover {
        background-color: #4a4a4a;
    }

    QPushButton:pressed {
        background-color: #2a2a2a;
    }

    QPushButton:disabled {
        background-color: #2a2a2a;
        color: #666666;
    }

    /* Специальные кнопки */
    QPushButton#startBtn {
        background-color: #007acc;
        color: white;
    }

    QPushButton#startBtn:hover {
        background-color: #1a8ad4;
    }

    QPushButton#startBtn:disabled {
        background-color: #1a3a5a;
        color: #6688aa;
    }

    QPushButton#stopBtn {
        background-color: #d32f2f;
        color: white;
    }

    QPushButton#stopBtn:hover {
        background-color: #e53935;
    }

    QPushButton#stopBtn:disabled {
        background-color: #4a1a1a;
        color: #886666;
    }

    QPushButton#drawBtn {
        background-color: #2d2d2d;
        color: #d4d4d4;
        border: 1px solid #3c3c3c;
        min-width: 100px;
    }

    QPushButton#drawBtn:hover {
        background-color: #3c3c3c;
    }

    QPushButton#drawBtn[class="active"] {
        background-color: #007acc;
        color: white;
        border-color: #007acc;
    }

    /* Поля ввода */
    QLineEdit {
        background-color: #2d2d2d;
        color: #d4d4d4;
        border: 1px solid #3c3c3c;
        border-radius: 4px;
        padding: 6px 10px;
    }

    QLineEdit:focus {
        border-color: #007acc;
    }

    /* Выпадающие списки */
    QComboBox {
        background-color: #2d2d2d;
        color: #d4d4d4;
        border: 1px solid #3c3c3c;
        border-radius: 4px;
        padding: 6px 10px;
        min-height: 25px;
    }

    QComboBox:hover {
        border-color: #007acc;
    }

    QComboBox::drop-down {
        border: none;
    }

    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #d4d4d4;
        margin-right: 5px;
    }

    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        color: #d4d4d4;
        border: 1px solid #3c3c3c;
        selection-background-color: #007acc;
    }

    /* Спинбоксы */
    QSpinBox {
        background-color: #2d2d2d;
        color: #d4d4d4;
        border: 1px solid #3c3c3c;
        border-radius: 4px;
        padding: 4px 8px;
    }

    QSpinBox:focus {
        border-color: #007acc;
    }

    /* Чекбоксы */
    QCheckBox {
        color: #d4d4d4;
        spacing: 8px;
    }

    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid #3c3c3c;
        background-color: #2d2d2d;
    }

    QCheckBox::indicator:checked {
        background-color: #007acc;
        border-color: #007acc;
    }

    QCheckBox::indicator:hover {
        border-color: #007acc;
    }

    /* Статус лейбл */
    QLabel#statusLabel {
        background-color: #2d2d2d;
        padding: 12px;
        border-radius: 6px;
        font-size: 16px;
        font-weight: bold;
        border: 1px solid #3c3c3c;
    }

    QLabel#statusLabel[class="recording"] {
        background-color: #4a1a1a;
        color: #ff6b6b;
        border-color: #d32f2f;
    }

    QLabel#statusLabel[class="saving"] {
        background-color: #3a3a1a;
        color: #ffd93d;
        border-color: #f9a825;
    }

    QLabel#statusLabel[class="ready"] {
        background-color: #1a3a2a;
        color: #66bb6a;
        border-color: #43a047;
    }

    /* Информация */
    QLabel#infoLabel {
        color: #888888;
        font-size: 12px;
        padding: 5px;
        background-color: #252526;
        border-radius: 4px;
    }

    /* ScrollBar */
    QScrollBar:vertical {
        background-color: #1e1e1e;
        width: 12px;
        border-radius: 6px;
    }

    QScrollBar::handle:vertical {
        background-color: #3c3c3c;
        border-radius: 6px;
        min-height: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #4a4a4a;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""