import random
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QSplitter, QFrame, QComboBox, QSlider, QCheckBox,
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient
from core.dialogs import show_info, show_success, show_warning, DetailDialog


class GaugeWidget(QWidget):
    def __init__(self, label="", max_val=100, color="#4fc3f7"):
        super().__init__()
        self._label = label; self._max = max_val; self._color = color; self._val = 0
        self.setMinimumSize(100, 80)
    def set_value(self, v): self._val = v; self.update()
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h = self.width(), self.height()
        if w < 20 or h < 20: painter.end(); return
        painter.fillRect(self.rect(), QColor("#0b1426"))
        cx, cy, r = w//2, h//2-10, min(w,h)//2-15
        painter.setPen(QPen(QColor("#1a3060"), 6))
        painter.drawArc(int(cx-r), int(cy-r), int(r*2), int(r*2), 180*16, 180*16)
        angle = int(180 * self._val / self._max)
        painter.setPen(QPen(QColor(self._color), 6))
        painter.drawArc(int(cx-r), int(cy-r), int(r*2), int(r*2), 180*16, angle*16)
        painter.setPen(QColor(self._color))
        painter.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        painter.drawText(int(cx-30), int(cy+8), f"{self._val:.0f}")
        painter.setPen(QColor("#8fa8c8"))
        painter.setFont(QFont("Microsoft YaHei", 8))
        painter.drawText(int(cx-30), int(cy-15), self._label)
        painter.end()


class LogCollectorModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._collecting = True; self._count = 0; self._errors = 0; self._rate = 0
        self._sources = {s:True for s in ["Syslog(514)","应用日志","数据库审计","网络设备","安全日志"]}
        self._build_ui()
        self._timer = QTimer(self); self._timer.timeout.connect(self._tick); self._timer.start(1500)

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16,12,16,12)
        # Title bar
        title_row = QHBoxLayout()
        title_row.addWidget(QLabel("🔄 采集控制台", styleSheet="font-size:16px;font-weight:bold;color:#4fc3f7;"))
        self._status_btn = QPushButton("●  运行中"); self._status_btn.setStyleSheet("color:#81c784;font-weight:bold;padding:6px 18px;")
        self._status_btn.clicked.connect(self._toggle)
        title_row.addStretch(); title_row.addWidget(self._status_btn)
        layout.addLayout(title_row)

        # Gauges row
        gauge_row = QHBoxLayout()
        self._gauge_rate = GaugeWidget("条/秒", 50, "#4fc3f7"); gauge_row.addWidget(self._gauge_rate)
        self._gauge_total = GaugeWidget("总采集(万)", 100, "#81c784"); gauge_row.addWidget(self._gauge_total)
        self._gauge_err = GaugeWidget("错误率%", 10, "#ff5252"); gauge_row.addWidget(self._gauge_err)
        self._gauge_storage = GaugeWidget("存储MB", 200, "#ffab40"); gauge_row.addWidget(self._gauge_storage)
        layout.addLayout(gauge_row)

        # Source toggles
        src_box = QGroupBox("采集源控制")
        src_grid = QHBoxLayout()
        self._src_toggles = {}
        for name in self._sources:
            cb = QCheckBox(name); cb.setChecked(True); cb.setStyleSheet("color:#e8edf5;padding:8px;")
            cb.stateChanged.connect(lambda st, n=name: self._toggle_source(n, st))
            self._src_toggles[name] = cb; src_grid.addWidget(cb)
        src_box.setLayout(src_grid); layout.addWidget(src_box)

        # Control buttons
        ctrl_row = QHBoxLayout()
        for t,s in [("⚡ 一键启动全部", self._start_all), ("⏹ 停止全部", self._stop_all),
                     ("📊 采集统计", self._stats), ("⚙ 采集配置", self._config),
                     ("🧹 重置计数器", self._reset)]:
            b = QPushButton(t); b.clicked.connect(s)
            if "启动" in t: b.setProperty("primary", True)
            ctrl_row.addWidget(b)
        ctrl_row.addStretch()
        layout.addLayout(ctrl_row)

        # Status cards
        stat_row = QHBoxLayout()
        self._status_labels = {}
        for name in self._sources:
            card = QFrame(); card.setStyleSheet("QFrame{background:#121e3a;border:1px solid #2a4070;border-radius:8px;}")
            cl = QVBoxLayout(card); cl.setContentsMargins(10,8,10,8)
            cl.addWidget(QLabel(name,styleSheet="color:#8fa8c8;font-size:10px;"))
            lbl = QLabel("🟢 正常"); lbl.setStyleSheet("color:#81c784;font-weight:bold;")
            cl.addWidget(lbl); self._status_labels[name] = lbl; stat_row.addWidget(card)
        layout.addLayout(stat_row)

    def _toggle(self):
        self._collecting = not self._collecting
        self._status_btn.setText("●  运行中" if self._collecting else "○  已暂停")
        self._status_btn.setStyleSheet("color:#81c784;font-weight:bold;padding:6px 18px;" if self._collecting else "color:#ffab40;font-weight:bold;padding:6px 18px;")

    def _toggle_source(self, name, state):
        self._sources[name] = state == 2
        self._status_labels[name].setText("🟢 正常" if state == 2 else "🔴 已关闭")
        self._status_labels[name].setStyleSheet("color:#81c784;font-weight:bold;" if state == 2 else "color:#ff5252;font-weight:bold;")

    def _start_all(self):
        for cb in self._src_toggles.values(): cb.setChecked(True)
        self._collecting = True; show_success(self,"启动","全部采集源已启动")
    def _stop_all(self):
        for cb in self._src_toggles.values(): cb.setChecked(False)
        self._collecting = False; show_warning(self,"停止","全部采集源已停止")
    def _stats(self):
        lines=[f"采集总量: {self._count}条",f"错误数: {self._errors}",f"采集速率: {self._rate}条/秒",
               f"运行时间: 2天3小时",f"活跃源: {sum(1 for v in self._sources.values() if v)}/5"]
        DetailDialog("统计","\n".join(lines),self).exec()
    def _config(self):
        show_info(self,"采集配置","缓冲大小: 1000条\n超时时间: 30秒\n重试次数: 3次\n编码: UTF-8")
    def _reset(self):
        self._count=0; self._errors=0; self._rate=0; show_success(self,"重置","计数器已清零")

    def _tick(self):
        if not self._collecting: return
        self._rate = random.randint(10,45); self._count += self._rate
        if random.random()<0.15: self._errors += 1
        self._gauge_rate.set_value(self._rate)
        self._gauge_total.set_value(min(100, self._count/1000))
        self._gauge_err.set_value(min(10, self._errors/max(1,self._count)*1000))
        self._gauge_storage.set_value(min(200, self._count*0.15))
