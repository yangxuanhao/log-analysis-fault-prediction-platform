from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QFormLayout, QComboBox, QTextEdit, QSplitter,
    QListWidget, QListWidgetItem,
)
from PyQt6.QtGui import QColor
from core.dialogs import show_info, show_success, DetailDialog


class ReportCenterModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._reports = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16,12,16,12)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget(); ll = QVBoxLayout(left); ll.setContentsMargins(0,0,0,0)

        # Report generation buttons
        gen_row = QHBoxLayout()
        for t, s in [("📊 日报", lambda:self._gen("日报")),("📈 周报", lambda:self._gen("周报")),
                     ("📉 月报", lambda:self._gen("月报")),("🔍 故障分析", lambda:self._gen("故障分析报告")),
                     ("📈 趋势分析", lambda:self._gen("趋势分析报告"))]:
            b = QPushButton(t); b.clicked.connect(s)
            if "日报" in t or "周报" in t: b.setProperty("primary", True)
            gen_row.addWidget(b)
        gen_row.addStretch()
        ll.addLayout(gen_row)

        # Report history
        self._report_list = QListWidget()
        self._report_list.setStyleSheet("QListWidget{background:#121e3a;border:1px solid #2a4070;border-radius:8px;}"
            "QListWidget::item{padding:10px 14px;border-bottom:1px solid #1a3060;}"
            "QListWidget::item:hover{background:#1a3060;}")
        ll.addWidget(self._report_list, 1)

        for buttons in [
            [("历史报告", self._history), ("定时生成", self._schedule), ("对比分析", self._compare), ("批量归档", self._archive)],
        ]:
            r = QHBoxLayout()
            for t, s in buttons:
                b = QPushButton(t); b.clicked.connect(s); r.addWidget(b)
            ll.addLayout(r)
        splitter.addWidget(left)

        right = QWidget(); rl = QVBoxLayout(right); rl.setContentsMargins(0,0,0,0)
        config_box = QGroupBox("报告配置")
        form = QFormLayout(config_box)
        self._tmpl_combo = QComboBox(); self._tmpl_combo.addItems(["日报","周报","月报","故障分析报告","趋势分析报告"])
        form.addRow("模板", self._tmpl_combo)
        self._fmt_combo = QComboBox(); self._fmt_combo.addItems(["PDF","HTML","Markdown","Excel","Word"])
        form.addRow("格式", self._fmt_combo)
        rl.addWidget(config_box)

        preview_box = QGroupBox("预览")
        self._preview = QTextEdit()
        self._preview.setReadOnly(True); self._preview.setPlaceholderText("生成报告后在此预览...")
        preview_box.setLayout(QVBoxLayout()); preview_box.layout().addWidget(self._preview)
        rl.addWidget(preview_box)
        splitter.addWidget(right); layout.addWidget(splitter, 1)

    def _gen(self, template):
        self._tmpl_combo.setCurrentText(template)
        content = [f"{template} - 智能分析报告", f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}", "",
                   "【数据概览】", f"  日志总量: {__import__('random').randint(50000,500000):,} 条",
                   f"  异常事件: {__import__('random').randint(10,200)} 次",
                   f"  告警总数: {__import__('random').randint(5,80)} 条"]
        self._preview.setText("\n".join(content))
        name = f"{template}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        self._reports.insert(0,{"名称":name,"类型":template,"时间":datetime.now().strftime('%Y-%m-%d %H:%M')})
        item = QListWidgetItem(f"  📄 {name} [{template}]")
        self._report_list.insertItem(0, item)
        show_success(self, "生成", f"{template}已生成")

    def _history(self):
        lines = ["历史报告:"] + [f"  {r.get('时间','')} {r.get('类型','')} - {r.get('名称','')}" for r in self._reports[:20]]
        if not self._reports: lines.append("  (无)")
        DetailDialog("历史","\n".join(lines),self).exec()
    def _schedule(self):
        show_info(self,"定时","日报 08:00 | 周报 周一09:00 | 月报 1日10:00")
    def _compare(self):
        lines = ["对比: 本周vs上周", "日志量: +12.5%↑", "异常: -8.3%↓", "告警: -15.2%↓", "MTTR: -22%↑ 改善"]
        DetailDialog("对比","\n".join(lines),self).exec()
    def _archive(self):
        show_success(self,"归档",f"已归档{len(self._reports)}份报告")
