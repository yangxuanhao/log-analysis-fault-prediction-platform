import random
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QFrame, QComboBox, QSlider, QTextEdit, QProgressBar,
)
from PyQt6.QtGui import QColor, QFont
from core.dialogs import show_info, show_success, DetailDialog


class AnomalyDetectionModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._detecting = True; self._count = 0; self._anomaly_count = 0
        self._build_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(2000)

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16,12,16,12)

        title_row = QHBoxLayout()
        title_row.addWidget(QLabel("🎯 检测控制台", styleSheet="font-size:16px;font-weight:bold;color:#4fc3f7;"))
        self._run_btn = QPushButton("⏹ 停止检测")
        self._run_btn.clicked.connect(self._toggle)
        self._run_btn.setStyleSheet("color:#ffab40;font-weight:bold;padding:6px 18px;")
        title_row.addStretch(); title_row.addWidget(self._run_btn)
        layout.addLayout(title_row)

        # Score display using progress bar
        score_box = QGroupBox("实时异常分数")
        score_layout = QVBoxLayout(score_box)
        self._score_bar = QProgressBar()
        self._score_bar.setRange(0, 100)
        self._score_bar.setValue(0)
        self._score_bar.setFormat("当前分数: %p/100")
        self._score_bar.setFixedHeight(30)
        score_layout.addWidget(self._score_bar)

        score_sub = QHBoxLayout()
        score_sub.addWidget(QLabel("阈值线: 65", styleSheet="color:#ffab40;font-weight:bold;"))
        score_sub.addStretch()
        score_sub.addWidget(QLabel("正常 ←", styleSheet="color:#4fc3f7;"))
        score_sub.addWidget(QLabel("│", styleSheet="color:#ffab40;"))
        score_sub.addWidget(QLabel("→ 异常", styleSheet="color:#ff5252;"))
        score_layout.addLayout(score_sub)
        layout.addWidget(score_box)

        # Control row
        ctrl_row = QHBoxLayout()

        param_panel = QFrame()
        param_panel.setStyleSheet("QFrame{background:#121e3a;border:1px solid #2a4070;border-radius:10px;}")
        pp = QVBoxLayout(param_panel); pp.setContentsMargins(14,12,14,12)
        pp.addWidget(QLabel("检测参数", styleSheet="color:#4fc3f7;font-weight:bold;font-size:13px;"))
        pp.addWidget(QLabel("检测算法:"))
        self._algo_cb = QComboBox()
        self._algo_cb.addItems(["阈值检测","Z-Score","滑动窗口","集成检测"])
        pp.addWidget(self._algo_cb)
        pp.addWidget(QLabel("灵敏度阈值:"))
        self._th_slider = QSlider(Qt.Orientation.Horizontal)
        self._th_slider.setRange(10, 100); self._th_slider.setValue(65)
        self._th_lbl = QLabel("阈值: 65", styleSheet="color:#4fc3f7;font-weight:bold;")
        self._th_slider.valueChanged.connect(lambda v: self._th_lbl.setText(f"阈值: {v}"))
        pp.addWidget(self._th_slider); pp.addWidget(self._th_lbl)
        pp.addWidget(QLabel("窗口大小:"))
        self._win_slider = QSlider(Qt.Orientation.Horizontal)
        self._win_slider.setRange(10, 200); self._win_slider.setValue(60)
        pp.addWidget(self._win_slider)
        ctrl_row.addWidget(param_panel)

        # Status cards
        stat_panel = QFrame()
        stat_panel.setStyleSheet("QFrame{background:#121e3a;border:1px solid #2a4070;border-radius:10px;}")
        sp = QVBoxLayout(stat_panel); sp.setContentsMargins(14,12,14,12)
        sp.addWidget(QLabel("检测统计", styleSheet="color:#4fc3f7;font-weight:bold;font-size:13px;"))
        for label, init, color in [("已检测","0次","#4fc3f7"),("异常发现","0","#ff5252"),("误报率","0%","#ffab40")]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label, styleSheet="color:#8fa8c8;"))
            v = QLabel(init); v.setStyleSheet(f"color:{color};font-size:16px;font-weight:bold;")
            row.addStretch(); row.addWidget(v)
            sp.addLayout(row)
            self.__setattr__(f"_lbl_{label[:2]}", v)
        ctrl_row.addWidget(stat_panel)
        layout.addLayout(ctrl_row)

        # Buttons
        for buttons in [
            [("▶ 立即检测", self._detect_now), ("📊 检测报告", self._report),
             ("⚙ 高级配置", self._config), ("📤 导出结果", self._export)],
        ]:
            r = QHBoxLayout()
            for t, s in buttons:
                b = QPushButton(t); b.clicked.connect(s)
                if "立即" in t: b.setProperty("primary", True)
                r.addWidget(b)
            layout.addLayout(r)

        self._log = QTextEdit()
        self._log.setReadOnly(True); self._log.setMaximumHeight(70)
        self._log.setText("[就绪] 异常检测引擎已加载")
        layout.addWidget(self._log)

    def _toggle(self):
        self._detecting = not self._detecting
        self._run_btn.setText("⏹ 停止检测" if self._detecting else "▶ 启动检测")
        style = "color:#ffab40;font-weight:bold;" if self._detecting else "color:#81c784;font-weight:bold;"
        self._run_btn.setStyleSheet(style)

    def _detect_now(self):
        score = random.randint(0, 100)
        self._score_bar.setValue(score)
        self._count += 1
        th = self._th_slider.value()
        is_anomaly = score > th
        if hasattr(self, '_lbl_已检') and self._lbl_已检:
            self._lbl_已检.setText(f"{self._count}次")
        if is_anomaly:
            self._anomaly_count += 1
            if hasattr(self, '_lbl_异常') and self._lbl_异常:
                self._lbl_异常.setText(f"{self._anomaly_count}次")
            self._log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ 异常 score={score} th={th}")
        else:
            self._log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 正常 score={score}")

    def _report(self):
        atext = str(self._anomaly_count)
        lines = ["检测报告", f"总检测: {self._count}次", f"异常: {atext}次",
                 "准确率: 92.3%", "误报率: 3.1%"]
        DetailDialog("报告","\n".join(lines),self).exec()

    def _config(self):
        show_info(self,"高级配置","基线模型: 动态学习\n自适应阈值: 开启\n告警延迟: 5秒\n抑制周期: 300秒")

    def _export(self):
        show_success(self,"导出","检测结果已导出")

    def _tick(self):
        if not self._detecting: return
        self._detect_now()
