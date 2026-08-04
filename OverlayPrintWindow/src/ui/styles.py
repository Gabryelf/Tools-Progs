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
"""

BUTTON_ICONS = {
    'draw': """
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="white" stroke-width="2"/>
            <path d="M2 17L12 22L22 17" stroke="white" stroke-width="2"/>
            <path d="M2 12L12 17L22 12" stroke="white" stroke-width="2"/>
        </svg>
    """,
    'clear': """
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M3 6H21" stroke="white" stroke-width="2"/>
            <path d="M8 6V4C8 3.44772 8.44772 3 9 3H15C15.5523 3 16 3.44772 16 4V6" stroke="white" stroke-width="2"/>
            <path d="M19 6L18 20C18 20.5523 17.5523 21 17 21H7C6.44772 21 6 20.5523 6 20L5 6" stroke="white" stroke-width="2"/>
        </svg>
    """,
    'undo': """
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M3 7L9 13L3 19" stroke="white" stroke-width="2" stroke-linecap="round"/>
            <path d="M9 7H15C17.2091 7 19 8.79086 19 11V11C19 13.2091 17.2091 15 15 15H3" stroke="white" stroke-width="2"/>
        </svg>
    """,
    'close': """
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M6 6L18 18M18 6L6 18" stroke="white" stroke-width="2" stroke-linecap="round"/>
        </svg>
    """
}