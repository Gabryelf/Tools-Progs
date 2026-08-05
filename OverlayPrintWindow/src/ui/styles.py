"""Стили интерфейса"""
PANEL_STYLE = """
QMainWindow {
    background: rgba(20, 20, 25, 240);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 30);
}
QWidget {
    background: transparent;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    color: #e0e0e0;
}
QPushButton {
    background: rgba(60, 60, 70, 180);
    border: none;
    border-radius: 8px;
    padding: 10px;
    color: #e0e0e0;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background: rgba(80, 80, 90, 200);
}
QPushButton:pressed {
    background: rgba(100, 100, 110, 200);
}
QPushButton.active {
    background: rgba(220, 60, 60, 180);
}
QPushButton.active:hover {
    background: rgba(240, 70, 70, 200);
}
QSlider::groove:horizontal {
    height: 4px;
    background: rgba(255, 255, 255, 20);
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: rgba(255, 255, 255, 150);
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: rgba(255, 255, 255, 200);
}
QLabel {
    color: rgba(200, 200, 200, 180);
    font-size: 12px;
}
QGroupBox {
    border: none;
    margin-top: 5px;
}
QGroupBox::title {
    color: rgba(200, 200, 200, 120);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QFrame[frameShape="4"] {
    background: rgba(255, 255, 255, 20);
    max-height: 1px;
}
"""

MINI_PANEL_STYLE = """
QMainWindow {
    background: rgba(20, 20, 25, 240);
    border-radius: 22px;
    border: 1px solid rgba(255, 255, 255, 20);
}
QWidget {
    background: transparent;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    color: #e0e0e0;
}
QPushButton {
    background: rgba(60, 60, 70, 150);
    border: none;
    border-radius: 6px;
    font-size: 12px;
    padding: 4px;
    color: #e0e0e0;
}
QPushButton:hover {
    background: rgba(80, 80, 90, 200);
}
QPushButton:checked {
    background: rgba(220, 60, 60, 180);
}
QLabel {
    color: rgba(200, 200, 200, 180);
    font-size: 10px;
}
"""