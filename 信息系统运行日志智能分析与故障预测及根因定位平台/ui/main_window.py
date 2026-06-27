from datetime import datetime
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QLinearGradient
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget,
    QPushButton, QFrame, QButtonGroup, QScrollArea,
)

from core.constants import APP_NAME, APP_VERSION, DEFAULT_WIDTH, DEFAULT_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from modules import MODULE_REGISTRY


class NavMenuButton(QPushButton):
    def __init__(self, index: int, icon: str, label: str, parent=None):
        super().__init__(parent)
        self._index = index
        self._icon = icon
        self._label = label
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(46)
        self.setText(f"  {icon}   {index:02d}  {label}")
        self._apply_style(False)

    def set_nav_active(self, active: bool) -> None:
        self.setChecked(active)
        self._apply_style(active)

    def _apply_style(self, active: bool) -> None:
        if active:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 rgba(79, 195, 247, 0.28), stop:1 rgba(30, 100, 200, 0.12));
                    color: #81d4fa;
                    border: none;
                    border-left: 3px solid #4fc3f7;
                    border-radius: 0 8px 8px 0;
                    text-align: left;
                    padding-left: 10px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #8fa8c8;
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 0 8px 8px 0;
                    text-align: left;
                    padding-left: 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: rgba(20, 42, 74, 0.7);
                    color: #e8edf5;
                    border-left: 3px solid #2a5a8a;
                }
            """)


class StaticSideNav(QWidget):
    module_selected = pyqtSignal(int)

    GROUPS = [
        ("日志采集与分析", [0, 1, 2, 3]),
        ("智能诊断与预测", [4, 5, 6, 7, 8]),
        ("监控与运维管理", [9, 10, 11, 12, 13]),
        ("系统配置与增强", [14, 15, 16, 17, 18, 19]),
    ]
    ICONS = ["📥", "🔍", "⚠", "🔎", "🔮", "🎯", "🔔", "🗺", "💊", "📊", "📄", "🧠", "📋", "🎓", "🛡", "🌐", "📨", "📐", "⚙", "🗄"]

    def __init__(self, modules: list, parent=None):
        super().__init__(parent)
        self._modules = modules
        self._buttons: list[NavMenuButton] = []
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)

        for gi, (group_name, indices) in enumerate(self.GROUPS):
            header = QLabel(group_name)
            header.setStyleSheet("""
                color: #6a8aaa;
                background: transparent;
                font-size: 11px;
                padding: 8px 12px 4px 14px;
                letter-spacing: 1px;
            """)
            layout.addWidget(header)

            for idx in indices:
                _, name, _ = self._modules[idx]
                btn = NavMenuButton(idx + 1, self.ICONS[idx], name)
                btn.clicked.connect(lambda checked, i=idx: (self.select_module(i), self.emit_selected(i)))
                self._group.addButton(btn, idx)
                self._buttons.append(btn)
                layout.addWidget(btn)

            if gi < len(self.GROUPS) - 1:
                sep = QFrame()
                sep.setFixedHeight(1)
                sep.setStyleSheet("background: rgba(30, 58, 95, 0.6); border: none; margin: 6px 12px;")
                layout.addWidget(sep)

        layout.addStretch()

    def select_module(self, index: int) -> None:
        for i, btn in enumerate(self._buttons):
            btn.set_nav_active(self._group.id(btn) == index)

    def emit_selected(self, index: int) -> None:
        self.module_selected.emit(index)


class NavPanel(QFrame):
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, QColor("#061020"))
        grad.setColorAt(0.5, QColor("#0a1a30"))
        grad.setColorAt(1, QColor("#081428"))
        painter.fillRect(self.rect(), grad)
        painter.setPen(QPen(QColor(79, 195, 247, 40), 1))
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        painter.end()


class TopBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(58)
        self._time_lbl = QLabel()
        self._time_lbl.setStyleSheet("color: #8fa8c8; background: transparent; font-size: 12px;")
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time)
        self._timer.start(1000)
        self._update_time()

    def _update_time(self) -> None:
        self._time_lbl.setText(datetime.now().strftime("%Y年%m月%d日  %H:%M:%S"))

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0, QColor("#0a1a30"))
        grad.setColorAt(0.5, QColor("#0e2040"))
        grad.setColorAt(1, QColor("#0a1a30"))
        painter.fillRect(self.rect(), grad)
        painter.setPen(QPen(QColor(79, 195, 247, 50), 1))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        painter.end()


class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self._lbl = QLabel("系统运行正常  ·  日志分析平台在线")
        self._lbl.setStyleSheet("color: #6a8aaa; background: transparent; font-size: 11px;")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        dot = QLabel("●")
        dot.setStyleSheet("color: #4fc3f7; background: transparent; font-size: 10px;")
        lay.addWidget(dot)
        lay.addWidget(self._lbl)
        lay.addStretch()
        ver = QLabel(f"版本 {APP_VERSION}")
        ver.setStyleSheet("color: #6a8aaa; background: transparent; font-size: 11px;")
        lay.addWidget(ver)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#061020"))
        painter.setPen(QPen(QColor(30, 58, 95), 1))
        painter.drawLine(0, 0, self.width(), 0)
        painter.end()


class ContentFrame(QFrame):
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#0a1628"))
        painter.setPen(QPen(QColor(79, 195, 247, 12)))
        step = 60
        for x in range(0, self.width(), step):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), step):
            painter.drawLine(0, y, self.width(), y)
        painter.end()


class MainWindow(QMainWindow):
    def __init__(self, username: str):
        super().__init__()
        self._username = username
        self.setWindowTitle(f"{APP_NAME} - v{APP_VERSION}")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self._modules: list[QWidget] = []
        self._build()

    def _build(self) -> None:
        central = QWidget()
        central.setStyleSheet("background: #0a1628;")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        nav_panel = NavPanel()
        nav_panel.setFixedWidth(240)
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(0, 16, 0, 14)
        nav_layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self._navigator = StaticSideNav(MODULE_REGISTRY)
        self._navigator.module_selected.connect(self._on_module_changed)
        scroll.setWidget(self._navigator)
        nav_layout.addWidget(scroll, 1)

        user_box = QFrame()
        user_box.setStyleSheet("""
            QFrame {
                background: rgba(20, 42, 74, 0.6);
                border: 1px solid #2a4070;
                border-radius: 8px;
                margin: 0 10px;
            }
        """)
        user_lay = QHBoxLayout(user_box)
        user_lay.setContentsMargins(10, 8, 10, 8)
        avatar = QLabel(self._username[0].upper() if self._username else "A")
        avatar.setFixedSize(30, 30)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #4fc3f7, stop:1 #1565c0);
            border-radius: 15px;
            color: #061220;
            font-weight: bold;
            font-size: 13px;
        """)
        user_info = QVBoxLayout()
        user_info.setSpacing(0)
        user_name = QLabel(self._username)
        user_name.setStyleSheet("color: #e8edf5; background: transparent; font-size: 12px; font-weight: bold;")
        user_role = QLabel("系统运维工程师")
        user_role.setStyleSheet("color: #6a8aaa; background: transparent; font-size: 10px;")
        user_info.addWidget(user_name)
        user_info.addWidget(user_role)
        user_lay.addWidget(avatar)
        user_lay.addLayout(user_info, 1)
        nav_layout.addWidget(user_box)

        logout_btn = QPushButton("退出登录")
        logout_btn.setProperty("danger", True)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(logout_btn.styleSheet() + "margin: 0 10px;")
        logout_btn.clicked.connect(self.close)
        nav_layout.addWidget(logout_btn)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        top_bar = TopBar()
        top_lay = QHBoxLayout(top_bar)
        top_lay.setContentsMargins(24, 0, 24, 0)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        self._module_title = QLabel(MODULE_REGISTRY[0][1])
        self._module_title.setFont(QFont("Microsoft YaHei", 15, QFont.Weight.Bold))
        self._module_title.setStyleSheet("color: #e8edf5; background: transparent;")
        breadcrumb = QLabel("首页  /  功能模块")
        breadcrumb.setStyleSheet("color: #6a8aaa; background: transparent; font-size: 11px;")
        self._breadcrumb = breadcrumb
        title_col.addWidget(self._module_title)
        title_col.addWidget(breadcrumb)
        top_lay.addLayout(title_col)
        top_lay.addStretch()

        status_row = QHBoxLayout()
        status_row.setSpacing(16)
        for dot_color, text in [("#4fc3f7", "日志采集"), ("#4fc3f7", "分析引擎"), ("#4fc3f7", "通信正常")]:
            item = QHBoxLayout()
            item.setSpacing(4)
            d = QLabel("●")
            d.setStyleSheet(f"color: {dot_color}; background: transparent; font-size: 9px;")
            t = QLabel(text)
            t.setStyleSheet("color: #6a8aaa; background: transparent; font-size: 11px;")
            item.addWidget(d)
            item.addWidget(t)
            status_row.addLayout(item)
        top_lay.addLayout(status_row)
        top_lay.addSpacing(20)
        top_lay.addWidget(top_bar._time_lbl)

        content_wrap = ContentFrame()
        content_lay = QVBoxLayout(content_wrap)
        content_lay.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent;")
        for _, name, cls in MODULE_REGISTRY:
            module = cls()
            self._modules.append(module)
            self._stack.addWidget(module)
        content_lay.addWidget(self._stack)

        status_bar = StatusBar()

        right.addWidget(top_bar)
        right.addWidget(content_wrap, 1)
        right.addWidget(status_bar)

        root.addWidget(nav_panel)
        root.addLayout(right, 1)

        self._navigator.select_module(0)
        self._navigator.emit_selected(0)

    def _on_module_changed(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        self._navigator.select_module(index)
        name = MODULE_REGISTRY[index][1]
        self._module_title.setText(name)
        self._breadcrumb.setText(f"首页  /  {name}")
