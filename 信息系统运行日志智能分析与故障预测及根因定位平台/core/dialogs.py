from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame,
)

from core.styles import BG_PANEL, ACCENT, TEXT_PRIMARY, TEXT_SECONDARY, BORDER, DANGER, WARN

_BTN_PRIMARY = """
    QPushButton {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1565c0, stop:1 #1e88e5);
        color: #ffffff;
        border: 1px solid #42a5f5;
        border-radius: 6px;
        padding: 8px 20px;
        font-size: 13px;
        font-weight: bold;
        min-height: 32px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1e88e5, stop:1 #42a5f5);
        color: #ffffff;
    }
    QPushButton:pressed {
        background: #0d47a1;
        color: #ffffff;
    }
"""

_BTN_SECONDARY = """
    QPushButton {
        background-color: #1f3060;
        color: #e8edf5;
        border: 1px solid #2a4070;
        border-radius: 6px;
        padding: 8px 20px;
        font-size: 13px;
        min-height: 32px;
    }
    QPushButton:hover {
        background-color: #25366a;
        border-color: #4fc3f7;
        color: #ffffff;
    }
"""

_BTN_DANGER = """
    QPushButton {
        background-color: #8b2030;
        color: #ffffff;
        border: 1px solid #ff5252;
        border-radius: 6px;
        padding: 8px 20px;
        font-size: 13px;
        font-weight: bold;
        min-height: 32px;
    }
    QPushButton:hover {
        background-color: #a82838;
        color: #ffffff;
    }
"""


def _style_button(btn: QPushButton, kind: str = "primary") -> None:
    styles = {"primary": _BTN_PRIMARY, "secondary": _BTN_SECONDARY, "danger": _BTN_DANGER}
    btn.setStyleSheet(styles.get(kind, _BTN_PRIMARY))
    btn.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold if kind != "secondary" else QFont.Weight.Normal))


class StyledDialog(QDialog):
    def __init__(self, title: str, message: str, dialog_type: str = "info", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._build(message, dialog_type)

    def _build(self, message: str, dialog_type: str) -> None:
        icons = {"info": "ℹ", "success": "✓", "warning": "⚠", "error": "✕"}
        colors = {"info": ACCENT, "success": "#81c784", "warning": WARN, "error": DANGER}
        icon = icons.get(dialog_type, "ℹ")
        color = colors.get(dialog_type, ACCENT)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)

        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 22))
        icon_label.setStyleSheet(f"color: {color}; background: transparent;")
        icon_label.setFixedWidth(40)
        title_label = QLabel(self.windowTitle())
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        header.addWidget(icon_label)
        header.addWidget(title_label, 1)
        layout.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background: {BORDER}; max-height: 1px; border: none;")
        layout.addWidget(line)

        body = QLabel(message)
        body.setWordWrap(True)
        body.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; padding: 4px 0;")
        layout.addWidget(body)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = QPushButton("确定")
        _style_button(ok_btn, "primary")
        ok_btn.setMinimumWidth(100)
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

        self.setStyleSheet(f"QDialog {{ background-color: {BG_PANEL}; border: 1px solid {BORDER}; }}")


class ConfirmDialog(QDialog):
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(440)
        self._result = False
        self._build(message)

    def _build(self, message: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)

        title_label = QLabel(self.windowTitle())
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {WARN}; background: transparent;")
        layout.addWidget(title_label)

        body = QLabel(message)
        body.setWordWrap(True)
        body.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        layout.addWidget(body)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("取消")
        _style_button(cancel_btn, "secondary")
        cancel_btn.setMinimumWidth(90)
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("确认")
        _style_button(ok_btn, "danger")
        ok_btn.setMinimumWidth(90)
        ok_btn.clicked.connect(self._on_confirm)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)
        self.setStyleSheet(f"QDialog {{ background-color: {BG_PANEL}; border: 1px solid {BORDER}; }}")

    def _on_confirm(self) -> None:
        self._result = True
        self.accept()

    @property
    def confirmed(self) -> bool:
        return self._result


class DetailDialog(QDialog):
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(520, 360)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)

        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ACCENT}; background: transparent;")
        layout.addWidget(title_label)

        editor = QTextEdit()
        editor.setReadOnly(True)
        editor.setPlainText(content)
        layout.addWidget(editor, 1)

        btn = QPushButton("关闭")
        _style_button(btn, "primary")
        btn.setMinimumWidth(100)
        btn.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(btn)
        layout.addLayout(row)
        self.setStyleSheet(f"QDialog {{ background-color: {BG_PANEL}; }}")


def show_info(parent, title: str, message: str) -> None:
    StyledDialog(title, message, "info", parent).exec()

def show_success(parent, title: str, message: str) -> None:
    StyledDialog(title, message, "success", parent).exec()

def show_warning(parent, title: str, message: str) -> None:
    StyledDialog(title, message, "warning", parent).exec()

def show_error(parent, title: str, message: str) -> None:
    StyledDialog(title, message, "error", parent).exec()

def ask_confirm(parent, title: str, message: str) -> bool:
    dlg = ConfirmDialog(title, message, parent)
    dlg.exec()
    return dlg.confirmed
