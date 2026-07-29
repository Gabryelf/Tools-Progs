"""
Стили для интерфейса приложения
"""

from tkinter import ttk
import tkinter as tk


class AppStyles:
    """Стили приложения"""

    @staticmethod
    def setup_styles():
        """Настройка стилей"""
        style = ttk.Style()

        # Основные цвета
        colors = {
            'primary': '#2196F3',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'danger': '#F44336',
            'dark': '#333333',
            'light': '#F5F5F5',
            'white': '#FFFFFF'
        }

        # Стиль для заголовка
        style.configure(
            'Title.TLabel',
            font=('Segoe UI', 18, 'bold'),
            foreground=colors['dark']
        )

        # Стиль для подзаголовка
        style.configure(
            'Subtitle.TLabel',
            font=('Segoe UI', 10),
            foreground='#666666'
        )

        # Стиль для кнопок
        style.configure(
            'Action.TButton',
            font=('Segoe UI', 10),
            padding=(20, 8)
        )

        # Стиль для статуса
        style.configure(
            'Status.TLabel',
            font=('Segoe UI', 10, 'italic'),
            foreground='#666666'
        )

        # Стиль для рамки настроек
        style.configure(
            'Settings.TLabelframe',
            font=('Segoe UI', 10, 'bold')
        )

        # Стиль для радиокнопок
        style.configure(
            'Language.TRadiobutton',
            font=('Segoe UI', 9)
        )

        # Стиль для чекбоксов
        style.configure(
            'Option.TCheckbutton',
            font=('Segoe UI', 9)
        )

        # Цветовая схема для прогресс-бара
        style.configure(
            'Progress.Horizontal.TProgressbar',
            troughcolor=colors['light'],
            background=colors['primary'],
            bordercolor=colors['primary'],
            lightcolor=colors['primary'],
            darkcolor=colors['primary']
        )

        return style

    @staticmethod
    def get_colors() -> dict:
        """Получение цветовой схемы"""
        return {
            'primary': '#2196F3',
            'primary_hover': '#1976D2',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'danger': '#F44336',
            'dark': '#333333',
            'light': '#F5F5F5',
            'white': '#FFFFFF',
            'gray': '#999999',
            'border': '#E0E0E0'
        }
