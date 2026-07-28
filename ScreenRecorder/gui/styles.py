# screen_recorder/gui/styles.py
"""
Стили для интерфейса
"""

MAIN_STYLE = """
    QWidget {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #f5f5f5, stop:1 #e8e8e8);
        font-family: 'Segoe UI', Arial;
    }
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
        min-height: 20px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
    QPushButton:disabled {
        background-color: #cccccc;
        color: #888888;
    }
    QPushButton#stopBtn {
        background-color: #f44336;
    }
    QPushButton#stopBtn:hover {
        background-color: #da190b;
    }
    QPushButton#stopBtn:disabled {
        background-color: #cccccc;
        color: #888888;
    }
    QPushButton#settingsBtn {
        background-color: #2196F3;
    }
    QPushButton#settingsBtn:hover {
        background-color: #0b7dda;
    }
    QLabel {
        font-size: 13px;
        color: #333333;
    }
    QLabel#statusLabel {
        font-size: 16px;
        font-weight: bold;
        padding: 5px;
        border-radius: 4px;
        background-color: white;
    }
    QLabel#titleLabel {
        font-size: 18px;
        font-weight: bold;
        color: #2c3e50;
    }
    QComboBox {
        padding: 5px;
        border: 1px solid #ccc;
        border-radius: 4px;
        background: white;
        min-height: 25px;
    }
    QComboBox:hover {
        border-color: #4CAF50;
    }
    QLineEdit {
        padding: 5px;
        border: 1px solid #ccc;
        border-radius: 4px;
        background: white;
    }
    QLineEdit:focus {
        border-color: #4CAF50;
    }
"""