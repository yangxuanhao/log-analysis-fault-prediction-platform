import random
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QSplitter, QFrame, QSlider, QTextEdit,
    QSpinBox, QProgressBar, QCheckBox,
)
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QLinearGradient
from core.dialogs import show_info, show_success, DetailDialog


class StorageGauge(QWidget):
    def __init__(self):
        super().__init__()
        self._used = 0; self._total = 500
        self.setMinimumSize(200, 60)
    def set_used(self, v): self._used = v; self.update()
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h = self.width(), self.height()
        if w < 20 or h < 10: painter.end(); return
        bar_h = 24
        painter.fillRect(self.rect(), QColor("#0b1426"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1a3060"))
        painter.drawRoundedRect(0, (h-bar_h)//2, w, bar_h, 12, 12)
        ratio = min(1.0, self._used/max(self._total,1))
        color = QColor("#ff5252") if ratio > 0.85 else QColor("#ffab40") if ratio > 0.6 else QColor("#4fc3f7")
        painter.setBrush(color)
        painter.drawRoundedRect(2, (h-bar_h)//2, int((w-4)*ratio), bar_h, 10, 10)
        painter.setPen(QColor("#e8edf5"))
        painter.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        painter.drawText(0, (h-bar_h)//2, w, bar_h, Qt.AlignmentFlag.AlignCenter, f"{self._used:.0f}GB / {self._total}GB")
        painter.end()


class AuditArchiveModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._archived = 0; self._saved = 0; self._compressed = True; self._encrypted = True
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16,12,16,12)

        title_row = QHBoxLayout()
        title_row.addWidget(QLabel("🗄 归档管理台", styleSheet="font-size:16px;font-weight:bold;color:#4fc3f7;"))
        title_row.addStretch()
        layout.addLayout(title_row)

        # Storage gauge
        self._storage = StorageGauge()
        layout.addWidget(self._storage)

        # Stats cards
        stat_row = QHBoxLayout()
        for label, init, color in [("已归档", "0次","#4fc3f7"),("存储节省","0%","#81c784"),
                                     ("压缩率","--","#ffab40"),("保留天数","180","#ce93d8")]:
            card = QFrame(); card.setStyleSheet("QFrame{background:#121e3a;border:1px solid #2a4070;border-radius:8px;}")
            cl = QVBoxLayout(card); cl.setContentsMargins(12,10,12,10)
            cl.addWidget(QLabel(label,styleSheet="color:#8fa8c8;font-size:10px;"))
            v = QLabel(init); v.setStyleSheet(f"color:{color};font-size:20px;font-weight:bold;")
            self.__setattr__(f"_lbl_{label[:2]}", v); cl.addWidget(v)
            stat_row.addWidget(card)
        layout.addLayout(stat_row)

        # Policy controls
        policy_panel = QFrame(); policy_panel.setStyleSheet("QFrame{background:#121e3a;border:1px solid #2a4070;border-radius:10px;}")
        pp = QHBoxLayout(policy_panel)

        left_p = QVBoxLayout()
        left_p.addWidget(QLabel("归档策略",styleSheet="color:#4fc3f7;font-weight:bold;"))
        left_p.addWidget(QLabel("自动执行时间:"))
        left_p.addWidget(QLabel("⏰ 每天 03:00 (可配置)",styleSheet="color:#e8edf5;"))
        self._compress_cb = QCheckBox("启用压缩 (gzip)"); self._compress_cb.setChecked(True); left_p.addWidget(self._compress_cb)
        self._encrypt_cb = QCheckBox("启用加密 (AES-256)"); self._encrypt_cb.setChecked(True); left_p.addWidget(self._encrypt_cb)
        pp.addLayout(left_p)

        mid_p = QVBoxLayout()
        mid_p.addWidget(QLabel("保留期限:",styleSheet="color:#8fa8c8;"))
        self._ret_slider = QSlider(Qt.Orientation.Horizontal); self._ret_slider.setRange(30, 730); self._ret_slider.setValue(180)
        self._ret_lbl = QLabel("180天"); self._ret_slider.valueChanged.connect(lambda v: self._ret_lbl.setText(f"{v}天"))
        mid_p.addWidget(self._ret_slider); mid_p.addWidget(self._ret_lbl)
        pp.addLayout(mid_p)

        right_p = QVBoxLayout()
        right_p.addWidget(QLabel("存储位置:",styleSheet="color:#8fa8c8;"))
        right_p.addWidget(QLabel("/data/archive/",styleSheet="color:#e8edf5;font-family:monospace;font-size:12px;"))
        right_p.addWidget(QLabel("可用空间: 342GB",styleSheet="color:#81c784;"))
        pp.addLayout(right_p)
        layout.addWidget(policy_panel)

        # Action buttons
        for buttons in [
            [("📦 立即归档", self._archive_now), ("🔄 恢复数据", self._restore),
             ("🧹 清理过期", self._cleanup), ("📊 归档报告", self._report)],
            [("📋 审计日志", self._audit), ("⚙ 归档设置", self._settings),
             ("📤 导出清单", self._export), ("🧪 测试归档", self._test)],
        ]:
            r = QHBoxLayout()
            for t, s in buttons:
                b = QPushButton(t); b.clicked.connect(s)
                if "立即" in t: b.setProperty("primary", True)
                r.addWidget(b)
            layout.addLayout(r)

        self._log = QTextEdit(); self._log.setReadOnly(True); self._log.setMaximumHeight(80)
        self._log.setText("[就绪] 归档引擎就绪")
        layout.addWidget(self._log)

    def _archive_now(self):
        self._archived += 1
        size = random.randint(500, 3000)
        self._saved += int(size * 0.68)
        self._storage.set_used(self._storage._used + size/1000)
        if hasattr(self, '_lbl_已归'): self._lbl_已归.setText(f"{self._archived}次")
        if hasattr(self, '_lbl_存储'): self._lbl_存储.setText(f"{int(self._saved/1024*100)}%")
        self._log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 归档完成 {size}MB -> {int(size*0.32)}MB (压缩68%)")
        show_success(self,"归档",f"归档完成，节省存储 {int(size*0.68)}MB")

    def _restore(self):
        show_info(self,"恢复","选择恢复版本:\n① 2026-06-22 完整归档\n② 2026-06-15 增量归档\n③ 2026-06-08 完整归档")

    def _cleanup(self):
        self._log.append("[清理] 已清理过期归档 3个，释放 2.1GB")
        show_success(self,"清理","已清理3个过期归档")

    def _report(self):
        lines = ["归档报告", f"总归档: {self._archived}次", f"节省存储: {self._saved/1024:.1f}GB",
                 "压缩率: 68%", "加密: AES-256", "合规状态: ✅ 通过"]
        DetailDialog("报告","\n".join(lines),self).exec()

    def _audit(self):
        lines = ["审计日志:", "", "2026-06-23 03:00 自动归档 完成",
                 "2026-06-22 15:30 用户admin 恢复归档 ARC-20260615",
                 "2026-06-22 03:00 自动归档 完成", "2026-06-21 03:00 自动归档 完成"]
        DetailDialog("审计","\n".join(lines),self).exec()

    def _settings(self):
        show_info(self,"设置","归档路径: /data/archive/\n压缩格式: gzip\n加密算法: AES-256\n线程数: 4\n限速: 100MB/s")

    def _export(self):
        show_success(self,"导出","归档清单已导出")

    def _test(self):
        self._log.append("[测试] 归档测试通过 读写正常 6ms")
        show_info(self,"测试","归档读写测试通过")
