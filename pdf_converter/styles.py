"""Figma-inspired stylesheet for the PDF to Markdown converter."""

COLORS = {
    "bg_primary": "#1E1E2E",
    "bg_secondary": "#2A2A3C",
    "bg_card": "#313244",
    "bg_input": "#3B3B50",
    "bg_hover": "#45455A",
    "accent": "#89B4FA",
    "accent_hover": "#74A8F7",
    "accent_pressed": "#5E9CF5",
    "success": "#A6E3A1",
    "warning": "#F9E2AF",
    "error": "#F38BA8",
    "text_primary": "#CDD6F4",
    "text_secondary": "#A6ADC8",
    "text_muted": "#6C7086",
    "border": "#45475A",
    "border_focus": "#89B4FA",
    "shadow": "rgba(0, 0, 0, 0.25)",
}

FIGMA_STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['bg_primary']};
}}

QWidget#centralWidget {{
    background-color: {COLORS['bg_primary']};
}}

QLabel {{
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
}}

QLabel#titleLabel {{
    font-size: 28px;
    font-weight: 700;
    color: {COLORS['text_primary']};
    padding: 0px;
    margin: 0px;
}}

QLabel#subtitleLabel {{
    font-size: 14px;
    font-weight: 400;
    color: {COLORS['text_secondary']};
    padding: 0px;
    margin: 0px;
}}

QLabel#sectionLabel {{
    font-size: 13px;
    font-weight: 600;
    color: {COLORS['text_secondary']};
    letter-spacing: 1px;
    padding: 0px;
    margin: 0px;
}}

QLabel#statusLabel {{
    font-size: 13px;
    color: {COLORS['text_muted']};
    padding: 4px 0px;
}}

QFrame#card {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 20px;
}}

QFrame#dropZone {{
    background-color: {COLORS['bg_card']};
    border: 2px dashed {COLORS['border']};
    border-radius: 16px;
    padding: 40px;
}}

QFrame#dropZone:hover {{
    border-color: {COLORS['accent']};
    background-color: {COLORS['bg_hover']};
}}

QPushButton#primaryButton {{
    background-color: {COLORS['accent']};
    color: {COLORS['bg_primary']};
    border: none;
    border-radius: 10px;
    padding: 12px 28px;
    font-size: 14px;
    font-weight: 600;
    min-height: 20px;
}}

QPushButton#primaryButton:hover {{
    background-color: {COLORS['accent_hover']};
}}

QPushButton#primaryButton:pressed {{
    background-color: {COLORS['accent_pressed']};
}}

QPushButton#primaryButton:disabled {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_muted']};
}}

QPushButton#secondaryButton {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 12px 28px;
    font-size: 14px;
    font-weight: 500;
    min-height: 20px;
}}

QPushButton#secondaryButton:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['text_muted']};
}}

QPushButton#secondaryButton:pressed {{
    background-color: {COLORS['bg_input']};
}}

QPushButton#iconButton {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px;
    font-size: 13px;
    min-width: 36px;
    min-height: 36px;
}}

QPushButton#iconButton:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

QLineEdit {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    selection-background-color: {COLORS['accent']};
    selection-color: {COLORS['bg_primary']};
}}

QLineEdit:focus {{
    border-color: {COLORS['accent']};
}}

QLineEdit:read-only {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
}}

QTextEdit {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 12px;
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    font-size: 13px;
    selection-background-color: {COLORS['accent']};
    selection-color: {COLORS['bg_primary']};
}}

QTextEdit:focus {{
    border-color: {COLORS['accent']};
}}

QProgressBar {{
    background-color: {COLORS['bg_input']};
    border: none;
    border-radius: 6px;
    text-align: center;
    color: {COLORS['text_primary']};
    font-size: 12px;
    font-weight: 500;
    min-height: 12px;
    max-height: 12px;
}}

QProgressBar::chunk {{
    background-color: {COLORS['accent']};
    border-radius: 6px;
}}

QCheckBox {{
    color: {COLORS['text_primary']};
    font-size: 13px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['border']};
    border-radius: 4px;
    background-color: {COLORS['bg_input']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent']};
    border-color: {COLORS['accent']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['accent']};
}}

QScrollBar:vertical {{
    background: {COLORS['bg_secondary']};
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['text_muted']};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['text_secondary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: {COLORS['bg_secondary']};
    height: 8px;
    margin: 0px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS['text_muted']};
    border-radius: 4px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {COLORS['text_secondary']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

QToolTip {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

QFileDialog {{
    background-color: {COLORS['bg_primary']};
}}

QSplitter::handle {{
    background-color: {COLORS['border']};
    width: 1px;
    margin: 8px 0px;
}}
"""
