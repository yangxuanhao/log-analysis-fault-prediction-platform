import math
import random
from PyQt6.QtCore import Qt, QTimer, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QRadialGradient, QFont, QPen
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QStackedWidget, QFrame, QGraphicsDropShadowEffect,
)

from core.constants import APP_NAME, APP_VERSION, DEFAULT_USERNAME, DEFAULT_PASSWORD
from core.auth import AuthManager
from core.dialogs import show_success, show_error
from core.styles import ACCENT, BG_DARK, TEXT_SECONDARY, ACCENT_GLOW, BORDER


class ParticleCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._particles: list[dict] = []
        self._nodes: list[dict] = []
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)
        self._init_particles()
        self._init_nodes()

    def _init_particles(self) -> None:
        for _ in range(120):
            self._particles.append({
                "x": random.uniform(0, 1),
                "y": random.uniform(0, 1),
                "vx": random.uniform(-0.0005, 0.0005),
                "vy": random.uniform(-0.0008, -0.0002),
                "size": random.uniform(1.0, 3.0),
                "alpha": random.uniform(0.1, 0.5),
                "phase": random.uniform(0, math.pi * 2),
                "hue": random.choice([0.55, 0.58, 0.62]),
            })

    def _init_nodes(self) -> None:
        for _ in range(16):
            self._nodes.append({
                "x": random.uniform(0.1, 0.9),
                "y": random.uniform(0.15, 0.85),
                "r": random.uniform(2, 5),
                "phase": random.uniform(0, math.pi * 2),
            })

    def _tick(self) -> None:
        self._phase += 0.03
        for p in self._particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["phase"] += 0.04
            if p["y"] < -0.05:
                p["y"] = 1.05
                p["x"] = random.uniform(0, 1)
            if p["x"] < 0 or p["x"] > 1:
                p["vx"] *= -1
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        grad = QLinearGradient(0, 0, w * 0.6, h)
        grad.setColorAt(0, QColor("#040d1a"))
        grad.setColorAt(0.4, QColor("#08182a"))
        grad.setColorAt(1, QColor("#0a2040"))
        painter.fillRect(self.rect(), grad)

        glow = QRadialGradient(w * 0.35, h * 0.45, w * 0.5)
        glow.setColorAt(0, QColor(79, 195, 247, 30))
        glow.setColorAt(0.6, QColor(30, 80, 160, 12))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), glow)

        scan_y = int((self._phase * 0.15 % 1.0) * h)
        scan_grad = QLinearGradient(0, scan_y - 40, 0, scan_y + 40)
        scan_grad.setColorAt(0, QColor(79, 195, 247, 0))
        scan_grad.setColorAt(0.5, QColor(79, 195, 247, 15))
        scan_grad.setColorAt(1, QColor(79, 195, 247, 0))
        painter.fillRect(0, scan_y - 40, w, 80, scan_grad)

        for i in range(5):
            cx = w * (0.1 + i * 0.18)
            cy = h * 0.45 + math.sin(self._phase + i * 0.8) * 25
            radius = 100 + i * 25
            color = QColor(79, 195, 247, 6 + i * 4)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(QPointF(cx, cy), radius, radius * 0.55)

        grid_pen = QPen(QColor(79, 195, 247, 10))
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)
        step = 48
        for x in range(0, w, step):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, step):
            painter.drawLine(0, y, w, y)

        if len(self._nodes) >= 2:
            painter.setPen(QPen(QColor(79, 195, 247, 30), 1))
            for i, n1 in enumerate(self._nodes):
                for n2 in self._nodes[i + 1:i + 3]:
                    x1, y1 = n1["x"] * w, n1["y"] * h
                    x2, y2 = n2["x"] * w, n2["y"] * h
                    dist = math.hypot(x2 - x1, y2 - y1)
                    if dist < w * 0.35:
                        pulse = 0.3 + 0.7 * abs(math.sin(self._phase + i))
                        painter.setPen(QPen(QColor(79, 195, 247, int(25 * pulse)), 1))
                        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        for n in self._nodes:
            nx, ny = n["x"] * w, n["y"] * h
            pulse = 0.5 + 0.5 * math.sin(self._phase + n["phase"])
            radial = QRadialGradient(nx, ny, n["r"] * 3)
            radial.setColorAt(0, QColor(129, 212, 250, int(180 * pulse)))
            radial.setColorAt(1, QColor(129, 212, 250, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(radial)
            painter.drawEllipse(QPointF(nx, ny), n["r"] * 2, n["r"] * 2)

        for p in self._particles:
            alpha = int(255 * p["alpha"] * (0.6 + 0.4 * math.sin(p["phase"])))
            painter.setBrush(QColor(79, 195, 247, alpha))
            painter.drawEllipse(QPointF(p["x"] * w, p["y"] * h), p["size"], p["size"])

        painter.end()


class StatCard(QFrame):
    def __init__(self, value: str, label: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 30, 58, 0.65);
                border: 1px solid rgba(79, 195, 247, 0.25);
                border-radius: 10px;
            }
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(2)
        v = QLabel(value)
        v.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        v.setStyleSheet(f"color: {ACCENT_GLOW}; background: transparent;")
        u = QLabel(label)
        u.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; font-size: 11px;")
        lay.addWidget(v)
        lay.addWidget(u)


class TabSwitch(QWidget):
    switched = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._index = 0
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self._login_tab = QPushButton("登 录")
        self._reg_tab = QPushButton("注 册")
        for btn in [self._login_tab, self._reg_tab]:
            btn.setFixedHeight(38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            lay.addWidget(btn)
        self._login_tab.clicked.connect(lambda: self._select(0))
        self._reg_tab.clicked.connect(lambda: self._select(1))
        self._update_style()

    def _select(self, index: int) -> None:
        self._index = index
        self._update_style()
        self.switched.emit(index)

    def _update_style(self) -> None:
        active = """
            QPushButton {
                background-color: rgba(79, 195, 247, 0.15);
                color: #81d4fa;
                border: none;
                border-bottom: 2px solid #4fc3f7;
                font-weight: bold;
                font-size: 13px;
            }
        """
        inactive = """
            QPushButton {
                background-color: transparent;
                color: #8fa8c8;
                border: none;
                border-bottom: 2px solid transparent;
                font-size: 13px;
            }
            QPushButton:hover { color: #e8edf5; }
        """
        self._login_tab.setStyleSheet(active if self._index == 0 else inactive)
        self._reg_tab.setStyleSheet(active if self._index == 1 else inactive)


class AuthForm(QWidget):
    login_success = pyqtSignal(str)

    def __init__(self, auth: AuthManager, parent=None):
        super().__init__(parent)
        self._auth = auth
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(16)

        logo_row = QHBoxLayout()
        logo = QLabel("◎")
        logo.setFixedSize(44, 44)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {ACCENT}, stop:1 #1565c0);
            border-radius: 22px;
            font-size: 20px;
            color: {BG_DARK};
        """)
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel(APP_NAME)
        title.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        title.setWordWrap(True)
        title.setStyleSheet(f"color: {ACCENT_GLOW}; background: transparent;")
        ver = QLabel(f"版本 {APP_VERSION}")
        ver.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; font-size: 11px;")
        title_col.addWidget(title)
        title_col.addWidget(ver)
        logo_row.addWidget(logo)
        logo_row.addLayout(title_col, 1)
        layout.addLayout(logo_row)

        self._tabs = TabSwitch()
        self._tabs.switched.connect(self._on_tab_switch)
        layout.addWidget(self._tabs)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._make_login_page())
        self._stack.addWidget(self._make_register_page())
        layout.addWidget(self._stack)

    def _on_tab_switch(self, index: int) -> None:
        self._stack.setCurrentIndex(index)

    def _input_style(self) -> str:
        return f"""
            QLineEdit {{
                background-color: rgba(31, 48, 96, 0.8);
                color: #e8edf5;
                border: 1px solid {BORDER};
                border-left: 3px solid {ACCENT};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ACCENT};
                border-left: 3px solid {ACCENT_GLOW};
            }}
        """

    def _apply_primary_btn(self, btn: QPushButton) -> None:
        btn.setFont(QFont("Microsoft YaHei", 15, QFont.Weight.Bold))
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1565c0, stop:1 #1e88e5);
                color: #ffffff;
                border: 1px solid #42a5f5;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1e88e5, stop:1 #42a5f5);
                color: #ffffff;
                border-color: #64b5f6;
            }
            QPushButton:pressed {
                background: #0d47a1;
                color: #ffffff;
            }
        """)

    def _make_login_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(page)
        lay.setSpacing(14)

        lay.addWidget(self._field_label("账号"))
        self._login_user = QLineEdit()
        self._login_user.setText(DEFAULT_USERNAME)
        self._login_user.setPlaceholderText("请输入账号")
        self._login_user.setStyleSheet(self._input_style())
        self._login_user.setMinimumHeight(42)
        lay.addWidget(self._login_user)

        lay.addWidget(self._field_label("密码"))
        self._login_pass = QLineEdit()
        self._login_pass.setText(DEFAULT_PASSWORD)
        self._login_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self._login_pass.setPlaceholderText("请输入密码")
        self._login_pass.setStyleSheet(self._input_style())
        self._login_pass.setMinimumHeight(42)
        self._login_pass.returnPressed.connect(self._do_login)
        lay.addWidget(self._login_pass)

        lay.addSpacing(6)
        login_btn = QPushButton("登 录")
        self._apply_primary_btn(login_btn)
        login_btn.setMinimumHeight(48)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self._do_login)
        lay.addWidget(login_btn)
        return page

    def _make_register_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(page)
        lay.setSpacing(12)

        for label_text, attr, placeholder in [
            ("新账号", "_reg_user", "至少3个字符"),
            ("密码", "_reg_pass", "至少6个字符"),
            ("确认密码", "_reg_confirm", "再次输入密码"),
        ]:
            lay.addWidget(self._field_label(label_text))
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            field.setStyleSheet(self._input_style())
            field.setMinimumHeight(40)
            if "密码" in label_text:
                field.setEchoMode(QLineEdit.EchoMode.Password)
            setattr(self, attr, field)
            lay.addWidget(field)
        self._reg_confirm.returnPressed.connect(self._do_register)

        lay.addSpacing(4)
        reg_btn = QPushButton("注 册")
        self._apply_primary_btn(reg_btn)
        reg_btn.setMinimumHeight(48)
        reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_btn.clicked.connect(self._do_register)
        lay.addWidget(reg_btn)
        return page

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; font-size: 12px;")
        return lbl

    def _do_login(self) -> None:
        ok, msg = self._auth.login(self._login_user.text(), self._login_pass.text())
        if ok:
            self.login_success.emit(self._login_user.text().strip())
        else:
            show_error(self, "登录失败", msg)

    def _do_register(self) -> None:
        ok, msg = self._auth.register(
            self._reg_user.text(), self._reg_pass.text(), self._reg_confirm.text()
        )
        if ok:
            show_success(self, "注册成功", msg)
            self._login_user.setText(self._reg_user.text().strip())
            self._tabs._select(0)
            self._stack.setCurrentIndex(0)
        else:
            show_error(self, "注册失败", msg)


class LoginWindow(QWidget):
    login_success = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._auth = AuthManager()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1000, 620)
        self.resize(1180, 720)
        self._build()

    def _build(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._canvas = ParticleCanvas()
        left_wrap = QVBoxLayout()
        left_wrap.setContentsMargins(52, 52, 52, 48)

        badge = QLabel("运行日志智能分析")
        badge.setStyleSheet(f"""
            color: {ACCENT};
            background: rgba(79, 195, 247, 0.1);
            border: 1px solid rgba(79, 195, 247, 0.3);
            border-radius: 14px;
            padding: 6px 16px;
            font-size: 12px;
            max-width: 180px;
        """)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_wrap.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        left_wrap.addSpacing(20)
        slogan = QLabel("信息系统运行日志\n智能分析与故障预测")
        slogan.setFont(QFont("Microsoft YaHei", 28, QFont.Weight.Bold))
        slogan.setStyleSheet("color: #e8edf5; background: transparent; line-height: 1.4;")
        left_wrap.addWidget(slogan)

        sub = QLabel("日志采集汇聚 · 故障预测 · 根因定位 · 智能告警")
        sub.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; font-size: 13px; margin-top: 8px;")
        left_wrap.addWidget(sub)

        left_wrap.addSpacing(24)
        features = QHBoxLayout()
        features.setSpacing(10)
        for text in ["日志解析", "故障预测", "根因分析"]:
            chip = QLabel(text)
            chip.setStyleSheet("""
                color: #8fa8c8;
                background: rgba(26, 42, 78, 0.6);
                border: 1px solid #2a4070;
                border-radius: 12px;
                padding: 5px 14px;
                font-size: 11px;
            """)
            features.addWidget(chip)
        features.addStretch()
        left_wrap.addLayout(features)

        left_wrap.addStretch()

        stat_row = QHBoxLayout()
        stat_row.setSpacing(14)
        for val, unit in [("15万+", "日志/秒"), ("128", "接入节点"), ("99.5%", "预测准确率")]:
            stat_row.addWidget(StatCard(val, unit))
        left_wrap.addLayout(stat_row)

        left_panel = QWidget()
        left_panel.setLayout(left_wrap)
        left_panel.setStyleSheet("background: transparent;")

        canvas_layout = QHBoxLayout(self._canvas)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.addWidget(left_panel, 1)
        root.addWidget(self._canvas, 1)

        card_outer = QFrame()
        card_outer.setFixedWidth(440)
        card_outer.setStyleSheet("QFrame { background: transparent; }")
        outer_lay = QVBoxLayout(card_outer)
        outer_lay.setContentsMargins(24, 40, 24, 40)
        outer_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(11, 20, 38, 0.92);
                border: 1px solid rgba(79, 195, 247, 0.2);
                border-radius: 16px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(79, 195, 247, 70))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        form = AuthForm(self._auth)
        form.login_success.connect(self.login_success.emit)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.addWidget(form)
        outer_lay.addWidget(card)
        root.addWidget(card_outer)
