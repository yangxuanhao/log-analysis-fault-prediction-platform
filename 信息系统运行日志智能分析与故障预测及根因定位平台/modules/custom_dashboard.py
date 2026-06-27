import random
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QTextEdit, QSplitter, QGridLayout, QFrame,
    QComboBox, QProgressBar, QColorDialog,
)
from PyQt6.QtGui import QColor, QFont

from core.dialogs import show_info, show_success, show_warning, DetailDialog


class DashboardWidget(QFrame):
    def __init__(self, title: str, widget_type: str, parent=None):
        super().__init__(parent)
        self._title = title
        self._type = widget_type
        self.setStyleSheet("QFrame { background: #121e3a; border: 1px solid #2a4070; border-radius: 8px; }")
        self.setMinimumSize(200, 150)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lbl = QLabel(f"📊 {title}")
        lbl.setStyleSheet("color: #4fc3f7; font-weight: bold;")
        lay.addWidget(lbl)

        if widget_type == "metric":
            val = QLabel(f"{random.randint(1000,99999)}")
            val.setFont(QFont("Microsoft YaHei", 28, QFont.Weight.Bold))
            val.setStyleSheet("color: #81c784;")
            lay.addWidget(val, alignment=Qt.AlignmentFlag.AlignCenter)
            unit = QLabel(random.choice(["条/秒", "次/分", "%", "ms"]))
            unit.setStyleSheet("color: #8fa8c8;")
            lay.addWidget(unit, alignment=Qt.AlignmentFlag.AlignCenter)
        elif widget_type == "progress":
            bar = QProgressBar(); bar.setRange(0, 100); bar.setValue(random.randint(30, 95))
            bar.setFormat(f"{title} %p%"); lay.addWidget(bar)
            val = QLabel(f"{random.randint(100,999)} / {random.randint(500,1000)}")
            val.setStyleSheet("color: #8fa8c8;"); lay.addWidget(val)
        elif widget_type == "status":
            for name, val in [("CPU", f"{random.uniform(20,90):.0f}%"),
                            ("内存", f"{random.uniform(40,85):.0f}%"),
                            ("磁盘", f"{random.uniform(30,95):.0f}%")]:
                row = QHBoxLayout()
                row.addWidget(QLabel(name))
                v = QLabel(val)
                vnum = float(val.rstrip('%')) if '%' in val else float(val)
                v.setStyleSheet(f"color: {'#ff5252' if vnum > 80 else '#4fc3f7'};")
                row.addWidget(v); row.addStretch(); lay.addLayout(row)
        elif widget_type == "chart":
            chart = QFrame()
            chart.setStyleSheet("QFrame { background: #0b1426; border: 1px solid #1a3060; border-radius: 4px; min-height: 60px; }")
            lay.addWidget(chart, 1)
            note = QLabel("[趋势图区域]"); note.setStyleSheet("color: #6a8aaa; font-size: 9px;")
            lay.addWidget(note)
        lay.addStretch()


class CustomDashboardModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dashboards = ["默认仪表盘", "运维总览", "性能监控", "业务看板"]
        self._widgets = [
            ("日志处理量", "metric"), ("系统健康度", "progress"),
            ("资源使用率", "status"), ("异常趋势", "chart"),
            ("API调用量", "metric"), ("存储使用率", "progress"),
            ("服务状态", "status"), ("响应时间", "chart"),
        ]
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("当前仪表盘:"))
        self._dash_combo = QComboBox()
        self._dash_combo.addItems(self._dashboards)
        toolbar.addWidget(self._dash_combo)
        for text, slot in [("➕ 新建", self._new_dash), ("💾 保存", self._save_dash),
                           ("📋 加载", self._load_dash), ("🗑 删除", self._del_dash)]:
            b = QPushButton(text); b.clicked.connect(slot)
            if text == "💾 保存": b.setProperty("primary", True)
            toolbar.addWidget(b)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Widget grid
        self._grid = QGridLayout()
        self._grid.setSpacing(10)
        self._render_grid()
        layout.addLayout(self._grid, 1)

        # Add widget bar
        add_row = QHBoxLayout()
        add_row.addWidget(QLabel("添加组件:"))
        self._widget_combo = QComboBox()
        self._widget_combo.addItems(["指标卡", "进度条", "状态面板", "趋势图", "告警列表"])
        add_row.addWidget(self._widget_combo)
        add_row.addWidget(QPushButton("➕ 添加", clicked=self._add_widget))
        add_row.addWidget(QPushButton("⚙ 编辑", clicked=self._edit_widget))
        add_row.addWidget(QPushButton("❌ 移除", clicked=self._remove_widget))
        add_row.addStretch()
        layout.addLayout(add_row)

        # Properties
        prop_row = QHBoxLayout()
        for text, slot in [("主题切换", self._switch_theme), ("刷新频率设置", self._set_refresh),
                           ("导出仪表盘", self._export), ("全屏展示", self._fullscreen)]:
            b = QPushButton(text); b.clicked.connect(slot); prop_row.addWidget(b)
        prop_row.addStretch()
        layout.addLayout(prop_row)

    def _render_grid(self):
        for i in reversed(range(self._grid.count())):
            self._grid.itemAt(i).widget().setParent(None)
        types = ["metric", "progress", "status", "chart"]
        for idx, (title, wtype) in enumerate(self._widgets):
            row, col = divmod(idx, 4)
            w = DashboardWidget(title, wtype)
            self._grid.addWidget(w, row, col)

    def _new_dash(self): show_info(self, "新建仪表盘", "输入新仪表盘名称:\n_________\n\n预设布局: 2列 | 3列 | 4列")
    def _save_dash(self): show_success(self, "已保存", f"仪表盘「{self._dash_combo.currentText()}」已保存")
    def _load_dash(self): show_info(self, "加载", "选择历史仪表盘版本:\n- 2026-06-23 10:00\n- 2026-06-22 10:00\n- 2026-06-21 10:00")
    def _del_dash(self):
        if len(self._dashboards) <= 1: show_warning(self, "提示", "至少保留一个仪表盘"); return
        self._dashboards.remove(self._dash_combo.currentText())
        self._dash_combo.clear(); self._dash_combo.addItems(self._dashboards)
        show_success(self, "已删除", "仪表盘已删除")
    def _add_widget(self):
        widget_types = {"指标卡": "metric", "进度条": "progress", "状态面板": "status", "趋势图": "chart", "告警列表": "metric"}
        wt = widget_types.get(self._widget_combo.currentText(), "metric")
        self._widgets.append((f"组件{len(self._widgets)+1}", wt))
        self._render_grid()
        show_success(self, "已添加", f"已添加「{self._widget_combo.currentText()}」组件")
    def _edit_widget(self): show_info(self, "编辑组件", "组件标题:\n数据源:\n刷新间隔:\n尺寸: 小/中/大")
    def _remove_widget(self):
        if not self._widgets: return
        self._widgets.pop()
        self._render_grid()
        show_info(self, "已移除", "最后一个组件已移除")
    def _switch_theme(self): show_info(self, "主题切换", "浅色主题 | 深色主题 | 专业主题 | 高对比度主题")
    def _set_refresh(self): show_info(self, "刷新频率设置", "自动刷新: 开启\n频率: 10秒 | 30秒 | 60秒 | 300秒")
    def _export(self):
        lines = ["自定义仪表盘导出", f"名称: {self._dash_combo.currentText()}", f"组件数: {len(self._widgets)}"]
        DetailDialog("导出", "\n".join(lines), self).exec()
    def _fullscreen(self): show_info(self, "全屏", "按 Esc 退出全屏模式")
