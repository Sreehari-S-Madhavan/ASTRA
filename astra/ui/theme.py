"""
ASTRA UI Theme & Global Styling
Futuristic dark aerospace workstation design system inspired by spacecraft medical consoles.
Deep navy/slate backgrounds, luminous cyan/blue telemetry accents, and high-visibility alert indicators.
"""
from astra.config import THEME

GLOBAL_STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {THEME['bg_dark']};
    color: {THEME['text_primary']};
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
}}

QWidget {{
    color: {THEME['text_primary']};
    font-size: 12px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: {THEME['bg_surface']};
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {THEME['border']};
    min-height: 20px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: {THEME['accent_cyan']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* PushButtons */
QPushButton {{
    background-color: {THEME['bg_card']};
    color: {THEME['text_primary']};
    border: 1px solid {THEME['border']};
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {THEME['bg_hover']};
    border-color: {THEME['accent_cyan']};
    color: {THEME['accent_cyan']};
}}
QPushButton:pressed {{
    background-color: {THEME['border']};
}}

QPushButton#primaryBtn {{
    background-color: {THEME['accent_blue']};
    border: 1px solid {THEME['accent_cyan']};
    color: #FFFFFF;
}}
QPushButton#primaryBtn:hover {{
    background-color: #1E64D8;
    box-shadow: 0 0 10px {THEME['accent_glow']};
}}

QPushButton#emergencyBtn {{
    background-color: #B71C1C;
    border: 1px solid {THEME['status_critical']};
    color: #FFFFFF;
    font-weight: bold;
    letter-spacing: 1px;
}}
QPushButton#emergencyBtn:hover {{
    background-color: {THEME['status_critical']};
}}

/* LineEdit / TextEdit / ComboBox */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {THEME['bg_surface']};
    color: {THEME['text_primary']};
    border: 1px solid {THEME['border']};
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: {THEME['accent_blue']};
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border-color: {THEME['accent_cyan']};
}}

/* QComboBox dropdown styling */
QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {THEME['bg_card']};
    color: {THEME['text_primary']};
    border: 1px solid {THEME['border']};
    selection-background-color: {THEME['bg_hover']};
    selection-color: {THEME['accent_cyan']};
}}

/* QTableWidget */
QTableWidget, QTableView {{
    background-color: {THEME['bg_surface']};
    gridline-color: {THEME['border']};
    border: 1px solid {THEME['border']};
    border-radius: 6px;
    color: {THEME['text_primary']};
    selection-background-color: {THEME['bg_hover']};
}}
QHeaderView::section {{
    background-color: {THEME['bg_card']};
    color: {THEME['text_secondary']};
    font-weight: bold;
    border: none;
    border-bottom: 1px solid {THEME['border']};
    padding: 6px 10px;
}}

/* QTabWidget */
QTabWidget::pane {{
    border: 1px solid {THEME['border']};
    background: {THEME['bg_surface']};
    border-radius: 6px;
}}
QTabBar::tab {{
    background: {THEME['bg_dark']};
    color: {THEME['text_secondary']};
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid {THEME['border']};
    border-bottom: none;
}}
QTabBar::tab:selected {{
    background: {THEME['bg_surface']};
    color: {THEME['accent_cyan']};
    border-top: 2px solid {THEME['accent_cyan']};
}}

/* QSlider */
QSlider::groove:horizontal {{
    height: 4px;
    background: {THEME['border']};
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {THEME['accent_cyan']};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {THEME['text_primary']};
    border: 2px solid {THEME['accent_cyan']};
    width: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}}
"""
