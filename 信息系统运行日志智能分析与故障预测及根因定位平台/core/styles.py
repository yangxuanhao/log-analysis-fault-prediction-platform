BG_DARK = "#0b1426"
BG_PANEL = "#121e3a"
BG_CARD = "#1a2a4e"
BG_INPUT = "#1f3060"
ACCENT = "#4fc3f7"
ACCENT_DIM = "#29b6f6"
ACCENT_GLOW = "#81d4fa"
TEXT_PRIMARY = "#e8edf5"
TEXT_SECONDARY = "#8fa8c8"
BORDER = "#2a4070"
WARN = "#ffab40"
DANGER = "#ff5252"

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
}}
QPushButton {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 14px;
    min-height: 28px;
}}
QLabel {{
    background: transparent;
    color: {TEXT_PRIMARY};
    border: none;
}}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: {ACCENT_DIM};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {ACCENT};
}}
QPushButton:hover {{
    background-color: #1f3a6a;
    border-color: {ACCENT_DIM};
}}
QPushButton:pressed {{
    background-color: #1565c0;
    color: #ffffff;
}}
QPushButton[primary="true"] {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1565c0, stop:1 #1e88e5);
    color: #ffffff;
    border: 1px solid #42a5f5;
    font-weight: bold;
    font-size: 13px;
}}
QPushButton[primary="true"]:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1e88e5, stop:1 #42a5f5);
    color: #ffffff;
    border-color: #64b5f6;
}}
QPushButton[primary="true"]:pressed {{
    background: #0d47a1;
    color: #ffffff;
}}
QPushButton[danger="true"] {{
    background-color: #4a1520;
    border: 1px solid {DANGER};
    color: #ffffff;
    font-weight: bold;
}}
QPushButton[danger="true"]:hover {{
    background-color: #6a2030;
    color: #ffffff;
}}
QTableWidget {{
    background-color: {BG_PANEL};
    alternate-background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    border-radius: 8px;
    selection-background-color: #1a3a6a;
    selection-color: {TEXT_PRIMARY};
}}
QTableWidget::item {{
    padding: 6px;
    border: none;
}}
QHeaderView::section {{
    background-color: {BG_CARD};
    color: {ACCENT};
    border: none;
    border-bottom: 1px solid {BORDER};
    border-right: 1px solid {BORDER};
    padding: 10px 8px;
    font-weight: bold;
}}
QHeaderView::section:last {{
    border-right: none;
}}
QTableCornerButton::section {{
    background-color: {BG_CARD};
    border: none;
}}
QScrollBar:vertical {{
    background: {BG_PANEL};
    width: 10px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    background: {BG_PANEL};
}}
QTabBar::tab {{
    background: {BG_CARD};
    color: {TEXT_SECONDARY};
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {BG_PANEL};
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 18px;
    background-color: {BG_PANEL};
    font-weight: bold;
    color: {ACCENT};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    background-color: {BG_PANEL};
}}
QProgressBar {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    background: {BG_INPUT};
    text-align: center;
    color: {TEXT_PRIMARY};
    height: 22px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {ACCENT_DIM}, stop:1 {ACCENT});
    border-radius: 5px;
}}
QSlider::groove:horizontal {{
    height: 6px;
    background: {BG_INPUT};
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    width: 16px;
    margin: -5px 0;
    background: {ACCENT};
    border-radius: 8px;
}}
QToolTip {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {ACCENT_DIM};
    padding: 6px;
    border-radius: 4px;
}}
"""
