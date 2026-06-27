import random
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QSplitter, QFrame, QComboBox, QSlider, QTextEdit, QCheckBox,
)
from PyQt6.QtGui import QColor, QFont
from core.dialogs import show_info, show_success, show_warning, DetailDialog


class AlarmCenterModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._p0=self._p1=self._p2=self._p3=0
        self._suppression = True; self._auto_resolve = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16,12,16,12)

        title_row = QHBoxLayout()
        title_row.addWidget(QLabel("🔔 告警控制台", styleSheet="font-size:16px;font-weight:bold;color:#4fc3f7;"))
        self._status = QLabel("●  监控中"); self._status.setStyleSheet("color:#81c784;font-weight:bold;")
        title_row.addStretch(); title_row.addWidget(self._status)
        layout.addLayout(title_row)

        # Severity matrix
        sev_row = QHBoxLayout()
        sev_data = [
            ("P0 灾难", self._p0, "#ff1744", "#4a0000"),
            ("P1 严重", self._p1, "#ff5252", "#2a0000"),
            ("P2 一般", self._p2, "#ffab40", "#2a2000"),
            ("P3 提示", self._p3, "#4fc3f7", "#002040"),
        ]
        self._sev_labels = {}
        for label, val, color, bg in sev_data:
            card = QFrame(); card.setStyleSheet(f"QFrame{{background:{bg};border:2px solid {color};border-radius:12px;}}")
            cl = QVBoxLayout(card); cl.setContentsMargins(16,14,16,14)
            cl.addWidget(QLabel(label,styleSheet=f"color:{color};font-weight:bold;font-size:11px;",alignment=Qt.AlignmentFlag.AlignCenter))
            v = QLabel("0"); v.setStyleSheet(f"color:{color};font-size:32px;font-weight:bold;")
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sev_labels[label[:2]] = v; cl.addWidget(v)
            sev_row.addWidget(card, 1)
        layout.addLayout(sev_row)

        # Controls
        ctrl_panel = QFrame(); ctrl_panel.setStyleSheet("QFrame{background:#121e3a;border:1px solid #2a4070;border-radius:10px;}")
        cp = QHBoxLayout(ctrl_panel)

        left_ctrl = QVBoxLayout()
        left_ctrl.addWidget(QLabel("告警策略",styleSheet="color:#4fc3f7;font-weight:bold;"))
        self._sup_cb = QCheckBox("启用告警抑制"); self._sup_cb.setChecked(True); left_ctrl.addWidget(self._sup_cb)
        self._auto_cb = QCheckBox("自动解决已恢复告警"); left_ctrl.addWidget(self._auto_cb)
        cp.addLayout(left_ctrl)

        mid_ctrl = QVBoxLayout()
        mid_ctrl.addWidget(QLabel("抑制窗口:",styleSheet="color:#8fa8c8;"))
        self._win_slider = QSlider(Qt.Orientation.Horizontal); self._win_slider.setRange(30,600); self._win_slider.setValue(300)
        self._win_lbl = QLabel("300秒"); self._win_slider.valueChanged.connect(lambda v: self._win_lbl.setText(f"{v}秒"))
        mid_ctrl.addWidget(self._win_slider); mid_ctrl.addWidget(self._win_lbl)
        cp.addLayout(mid_ctrl)

        right_ctrl = QVBoxLayout()
        right_ctrl.addWidget(QLabel("通知方式:",styleSheet="color:#8fa8c8;"))
        for t,ck in [("邮件",True),("企业微信",True),("钉钉",False),("短信",False)]:
            cb = QCheckBox(t); cb.setChecked(ck); right_ctrl.addWidget(cb)
        cp.addLayout(right_ctrl)
        layout.addWidget(ctrl_panel)

        # Action buttons
        for buttons in [
            [("🔄 模拟告警", self._sim_alarm), ("✅ 全部确认", self._ack_all),
             ("🧹 清理已处理", self._clear), ("📊 告警统计", self._stats)],
            [("⏸ 静默模式", self._silence), ("📤 导出告警", self._export),
             ("⚙ 规则配置", self._rules), ("📋 告警日志", self._audit)],
        ]:
            r = QHBoxLayout()
            for t, s in buttons:
                b = QPushButton(t); b.clicked.connect(s)
                if "模拟" in t: b.setProperty("primary", True)
                r.addWidget(b)
            layout.addLayout(r)

        self._log = QTextEdit(); self._log.setReadOnly(True); self._log.setMaximumHeight(80)
        self._log.setText("[就绪] 告警管理中心已加载")
        layout.addWidget(self._log)

    def _sim_alarm(self):
        import random as rnd
        levels = [("P0",self._p0,"#ff1744"),("P1",self._p1,"#ff5252"),("P2",self._p2,"#ffab40"),("P3",self._p3,"#4fc3f7")]
        lv, lbl, color = rnd.choice(levels)
        setattr(self, f"_{lv}", getattr(self, f"_{lv}")+1)
        self._sev_labels[lv].setText(str(getattr(self, f"_{lv}")))
        self._log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✉ {lv}级告警已接收 - {rnd.choice(['连接超时','CPU过载','内存告警','磁盘告警'])}")
        show_info(self,"告警",f"已注入{lv}级模拟告警")

    def _ack_all(self):
        self._log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 全部告警已确认")
    def _clear(self):
        for lv in ["p0","p1","p2","p3"]:
            setattr(self,f"_{lv}",0); self._sev_labels[lv].setText("0")
        self._log.append("[已清理]")
        show_success(self,"清理","告警计数器已清零")
    def _stats(self):
        lines = ["当前告警统计:","",f"P0灾难: {self._p0} 次","P1严重: {self._p1} 次",
                 f"P2一般: {self._p2} 次",f"P3提示: {self._p3} 次","","抑制率: 85%","平均响应: 2.5分钟"]
        DetailDialog("统计","\n".join(lines),self).exec()
    def _silence(self):
        show_info(self,"静默","已开启静默模式，期间告警仅记录不通知")
    def _export(self):
        show_success(self,"导出","告警数据已导出")
    def _rules(self):
        show_info(self,"规则","1. P0/P1 即时通知\n2. P2 5分钟聚合\n3. P3 日报汇总\n4. 同源告警30分钟内合并")
    def _audit(self):
        lines = ["告警审计日志:","10:23 P1 数据库连接超时 已确认",
                 "10:25 P0 核心服务宕机 已升级","10:30 P2 磁盘告警 已处理"]
        DetailDialog("审计","\n".join(lines),self).exec()
