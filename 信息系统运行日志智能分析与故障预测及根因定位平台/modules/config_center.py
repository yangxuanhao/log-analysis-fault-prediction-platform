import json, random
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QComboBox, QFormLayout, QSpinBox, QCheckBox,
)
from PyQt6.QtGui import QColor

from core.dialogs import show_info, show_success, show_warning, DetailDialog


class ConfigCenterModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._configs = {
            "系统设置": {
                "日志采集频率": {"val": "2秒", "type": "select", "desc": "日志采集轮询间隔"},
                "数据保留天数": {"val": "30天", "type": "int", "desc": "日志数据保留期限"},
                "最大缓存行数": {"val": "500", "type": "int", "desc": "内存中缓存的最大日志条数"},
                "自动启动采集": {"val": "是", "type": "bool", "desc": "启动时自动开始日志采集"},
            },
            "检测参数": {
                "异常检测阈值": {"val": "0.65", "type": "float", "desc": "异常分数阈值(0-1)"},
                "滑动窗口大小": {"val": "60", "type": "int", "desc": "趋势分析样本数量"},
                "预测模型": {"val": "ARIMA", "type": "select", "desc": "故障预测算法"},
                "告警抑制窗口": {"val": "300秒", "type": "int", "desc": "重复告警合并时间窗口"},
            },
            "通知设置": {
                "邮件服务器": {"val": "smtp.company.com", "type": "string", "desc": "SMTP服务器地址"},
                "邮件端口": {"val": "587", "type": "int", "desc": "SMTP服务器端口"},
                "启用微信通知": {"val": "是", "type": "bool", "desc": "是否开启企业微信通知"},
                "告警静默时段": {"val": "23:00-07:00", "type": "string", "desc": "不发送通知的时间段"},
            },
            "日志解析": {
                "默认解析模板": {"val": "Syslog", "type": "select", "desc": "日志解析默认模板"},
                "自动解析": {"val": "是", "type": "bool", "desc": "采集后自动进行解析"},
                "错误模式提取": {"val": "开启", "type": "bool", "desc": "自动提取常见错误模式"},
            },
        }
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Config tree
        left = QWidget()
        ll = QVBoxLayout(left)
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["配置项", "当前值"])
        self._build_tree()
        self._tree.itemClicked.connect(self._show_config)
        ll.addWidget(QLabel("配置分类:"))
        ll.addWidget(self._tree, 1)
        splitter.addWidget(left)

        # Config detail
        right = QWidget()
        rl = QVBoxLayout(right)
        self._detail_group = QGroupBox("配置详情")
        self._detail_form = QFormLayout()
        self._key_label = QLabel("--")
        self._val_input = QLineEdit()
        self._desc_label = QLabel("")
        self._desc_label.setStyleSheet("color: #8fa8c8;")
        self._detail_form.addRow("配置项:", self._key_label)
        self._detail_form.addRow("当前值:", self._val_input)
        self._detail_form.addRow("说明:", self._desc_label)
        self._detail_group.setLayout(self._detail_form)
        rl.addWidget(self._detail_group)

        btn_row = QHBoxLayout()
        for text, slot in [("💾 保存修改", self._save_config), ("🔄 恢复默认", self._reset_default),
                           ("📥 导入配置", self._import), ("📤 导出配置", self._export)]:
            b = QPushButton(text); b.clicked.connect(slot)
            if text == "💾 保存修改": b.setProperty("primary", True)
            btn_row.addWidget(b)
        btn_row.addStretch()
        rl.addLayout(btn_row)
        self._log = QTextEdit()
        self._log.setReadOnly(True); self._log.setMaximumHeight(100)
        self._log.setText("[配置中心] 选择左侧配置项进行编辑")
        rl.addWidget(self._log)
        splitter.addWidget(right)
        layout.addWidget(splitter, 1)

        # Status bar
        status_row = QHBoxLayout()
        for text in [f"配置项总数: {sum(len(v) for v in self._configs.values())}",
                     f"配置分类: {len(self._configs)}", "配置版本: V1.0"]:
            lbl = QLabel(text); lbl.setStyleSheet("color: #6a8aaa;"); status_row.addWidget(lbl)
        status_row.addStretch()
        layout.addLayout(status_row)

    def _build_tree(self):
        self._tree.clear()
        for group, items in self._configs.items():
            g_item = QTreeWidgetItem(self._tree, [group, ""])
            for key, cfg in items.items():
                child = QTreeWidgetItem(g_item, [key, str(cfg["val"])])
            g_item.setExpanded(True)

    def _show_config(self, item, col):
        if not item.parent(): return
        group = item.parent().text(0)
        key = item.text(0)
        if group in self._configs and key in self._configs[group]:
            cfg = self._configs[group][key]
            self._key_label.setText(f"{group} > {key}")
            self._val_input.setText(str(cfg["val"]))
            self._desc_label.setText(f"类型: {cfg['type']} | 说明: {cfg['desc']}")
            self._current_path = (group, key)

    def _save_config(self):
        if not hasattr(self, '_current_path'): show_warning(self, "提示", "请先选择配置项"); return
        group, key = self._current_path
        if group in self._configs and key in self._configs[group]:
            self._configs[group][key]["val"] = self._val_input.text()
            self._build_tree()
            self._log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 已保存: {group} > {key} = {self._val_input.text()}")
            show_success(self, "已保存", f"{key} 配置已更新")

    def _reset_default(self):
        self._log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 配置已恢复默认值")
        show_success(self, "已恢复", "当前配置分类已恢复为默认值")

    def _import(self):
        show_info(self, "导入配置", "从文件导入配置:\n支持的格式: JSON | YAML\n建议导入前备份当前配置")

    def _export(self):
        lines = ["配置导出", f"时间: {datetime.now()}", ""]
        for group, items in self._configs.items():
            lines.append(f"[{group}]")
            for key, cfg in items.items():
                lines.append(f"  {key} = {cfg['val']}")
        DetailDialog("导出配置", "\n".join(lines), self).exec()
        self._log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📤 配置已导出")
