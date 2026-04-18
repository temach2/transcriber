"""
GUI Styles Module
Styles and themes for the Windows desktop interface.
"""

import customtkinter as ctk
from typing import Dict, Any

# Цветовая схема ( Anthropic-style)
COLORS = {
    'primary': '#6366f1',      # Индиговый
    'primary_dark': '#4f46e5',
    'primary_light': '#818cf8',
    'accent': '#0ea5e9',       # Голубой
    'background': '#f8fafc',
    'surface': '#ffffff',
    'border': '#e2e8f0',
    'text_primary': '#1e293b',
    'text_secondary': '#64748b',
    'text_inverse': '#ffffff',
    'success': '#22c55e',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'code_bg': '#f1f5f9',
    'list_hover': '#f1f5f9',
}

# Стили виджетов
STYLES = {
    'button_primary': {
        'fg_color': COLORS['primary'],
        'hover_color': COLORS['primary_dark'],
        'text_color': COLORS['text_inverse'],
        'font': ('Segoe UI', 12),
        'corner_radius': 8,
    },
    'button_secondary': {
        'fg_color': COLORS['surface'],
        'hover_color': COLORS['border'],
        'text_color': COLORS['text_primary'],
        'font': ('Segoe UI', 12),
        'corner_radius': 8,
        'border_width': 1,
        'border_color': COLORS['border'],
    },
    'button_danger': {
        'fg_color': COLORS['error'],
        'hover_color': '#dc2626',
        'text_color': COLORS['text_inverse'],
        'font': ('Segoe UI', 12),
        'corner_radius': 8,
    },
    'entry': {
        'fg_color': COLORS['surface'],
        'text_color': COLORS['text_primary'],
        'border_color': COLORS['border'],
        'placeholder_text_color': COLORS['text_secondary'],
        'font': ('Segoe UI', 12),
        'corner_radius': 8,
        'border_width': 1,
    },
    'frame': {
        'fg_color': COLORS['surface'],
        'corner_radius': 12,
        'border_width': 1,
        'border_color': COLORS['border'],
    },
    'label': {
        'text_color': COLORS['text_primary'],
        'font': ('Segoe UI', 12),
    },
    'label_large': {
        'text_color': COLORS['text_primary'],
        'font': ('Segoe UI', 16, 'bold'),
    },
    'label_small': {
        'text_color': COLORS['text_secondary'],
        'font': ('Segoe UI', 10),
    },
    'combobox': {
        'fg_color': COLORS['surface'],
        'text_color': COLORS['text_primary'],
        'border_color': COLORS['border'],
        'button_color': COLORS['border'],
        'button_hover_color': COLORS['border'],
        'dropdown_hover_color': COLORS['list_hover'],
        'font': ('Segoe UI', 12),
        'corner_radius': 8,
    },
    'checkbox': {
        'fg_color': COLORS['primary'],
        'border_color': COLORS['border'],
        'checkmark_color': COLORS['text_inverse'],
        'hover_color': COLORS['primary_light'],
    },
}


def apply_app_theme(root: ctk.CTk):
    """
    Применить тему к приложению.

    Args:
        root: Корневой виджет приложения
    """
    # Настройка цветовой схемы
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # Настройка окна
    root.configure(fg_color=COLORS['background'])

    # Центрирование
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')


def get_button_style(style_name: str) -> Dict[str, Any]:
    """
    Получить стиль кнопки по имени.

    Args:
        style_name: Имя стиля

    Returns:
        Словарь с параметрами стиля
    """
    return STYLES.get(style_name, STYLES['button_primary'])


def get_entry_style() -> Dict[str, Any]:
    """
    Получить стиль entry по умолчанию.

    Returns:
        Словарь с параметрами стиля
    """
    return STYLES['entry']


def get_frame_style() -> Dict[str, Any]:
    """
    Получить стиль frame по умолчанию.

    Returns:
        Словарь с параметрами стиля
    """
    return STYLES['frame']
