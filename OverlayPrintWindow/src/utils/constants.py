"""Константы приложения"""
# Цвета
COLORS = {
    'red': (255, 50, 50),
    'green': (50, 255, 50),
    'blue': (50, 150, 255),
    'yellow': (255, 255, 50),
    'purple': (200, 50, 255),
    'orange': (255, 150, 50),
    'white': (255, 255, 255),
    'pink': (255, 100, 200),
}

# Настройки пера по умолчанию
DEFAULT_PEN = {
    'color': (255, 50, 50),
    'width': 6,
    'alpha': 255
}

# Размеры панели
PANEL_WIDTH = 320
PANEL_HEIGHT = 420
MINI_PANEL_WIDTH = 180
MINI_PANEL_HEIGHT = 45

# Горячие клавиши
HOTKEYS = {
    'toggle_mode': 'F2',
    'exit': 'ESC',
    'fade': 'F4',
    'free': 'F',
    'line': 'L',
    'rectangle': 'R',
    'circle': 'C',
    'triangle': 'T',
}

# Настройки затухания
FADING = {
    'enabled': False,
    'delay': 3.0,  # Секунд до начала затухания
    'fade_duration': 3.0,  # Секунд на затухание
}

APP_NAME = "Overlay Marker"
