import random
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QTextEdit, QSplitter, QListWidget, QListWidgetItem,
    QLineEdit, QComboBox, QFormLayout, QCheckBox, QSpinBox,
)
from PyQt6.QtGui import QColor

from core.dialogs import show_info, show_success, show_warning, DetailDialog


class AlertNotifyModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._channels = [
            {"name": "邮件通知", "type": "email", "enabled": True, "config": "smtp.company.com:587"},
            {"name": "企业微信", "type": "wechat", "enabled": True, "config": "Webhook URL已配置"},
            {"name": "钉钉通知", "type": "dingtalk", "enabled": False, "config": "未配置"},
            {"name": "短信告警", "type": "sms", "enabled": False, "config": "未配置"},
            {"name": "Webhook回调", "type": "webhook", "enabled": True, "config": "https://hooks.example.com/alert"},
        ]
        self._rules = [
            {"name": "P0灾难告警即时通知", "level": "P0", "channels": "邮件+企业微信+短信", "enabled": True},
            {"name": "P1严重告警5分钟通知", "level": "P1", "channels": "邮件+企业微信", "enabled": True},
            {"name": "P2一般告警邮件通知", "level": "P2", "channels": "邮件", "enabled": True},
            {"name": "P3提示级告警汇总通知", "level": "P3", "channels": "日报汇总", "enabled": False},
        ]
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        # Channel status
        channel_row = QHBoxLayout()
        for ch in self._channels:
            card = QGroupBox(ch["name"])
            card.setFixedWidth(180)
            cl = QVBoxLayout(card)
            icon = {"email": "📧", "wechat": "💬", "dingtalk": "🔔", "sms": "📱", "webhook": "🔗"}
            lbl_icon = QLabel(icon.get(ch["type"], "📨"))
            lbl_icon.setFont(lbl_icon.font() or QLabel().font())
            lbl_icon.setStyleSheet("font-size: 24px;")
            lbl_status = QLabel("✅ 已启用" if ch["enabled"] else "❌ 未启用")
            lbl_status.setStyleSheet(f"color: {'#81c784' if ch['enabled'] else '#ff5252'};")
            lbl_config = QLabel(ch["config"])
            lbl_config.setStyleSheet("color: #8fa8c8; font-size: 9px;")
            cl.addWidget(lbl_icon, alignment=Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(lbl_status, alignment=Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(lbl_config)
            channel_row.addWidget(card)
        layout.addLayout(channel_row)

        # Config form
        splitter = QSplitter(Qt.Orientation.Horizontal)
        form_widget = QWidget()
        form = QFormLayout(form_widget)
        self._channel_combo = QComboBox()
        self._channel_combo.addItems([c["name"] for c in self._channels])
        form.addRow("通知通道", self._channel_combo)
        self._server_input = QLineEdit("smtp.company.com")
        form.addRow("服务器地址", self._server_input)
        self._port_spin = QSpinBox(); self._port_spin.setRange(1, 65535); self._port_spin.setValue(587)
        form.addRow("端口", self._port_spin)
        self._token_input = QLineEdit("********")
        form.addRow("Token/密钥", self._token_input)
        self._test_btn = QPushButton("📨 发送测试通知")
        self._test_btn.clicked.connect(self._test_notify)
        form.addRow("", self._test_btn)
        self._save_btn = QPushButton("💾 保存配置")
        self._save_btn.setProperty("primary", True)
        self._save_btn.clicked.connect(self._save_config)
        form.addRow("", self._save_btn)
        splitter.addWidget(form_widget)

        # Rules list
        rules_widget = QWidget()
        rl = QVBoxLayout(rules_widget)
        rl.addWidget(QLabel("通知规则:"))
        self._rules_list = QListWidget()
        for rule in self._rules:
            icon = "✅" if rule["enabled"] else "⏸"
            item = QListWidgetItem(f"{icon} [{rule['level']}] {rule['name']} → {rule['channels']}")
            self._rules_list.addItem(item)
        rl.addWidget(self._rules_list)
        rule_btn_row = QHBoxLayout()
        for text, slot in [("新建规则", self._new_rule), ("编辑规则", self._edit_rule),
                           ("启用/禁用", self._toggle_rule), ("删除规则", self._del_rule)]:
            b = QPushButton(text); b.clicked.connect(slot); rule_btn_row.addWidget(b)
        rl.addLayout(rule_btn_row)
        splitter.addWidget(rules_widget)
        layout.addWidget(splitter, 1)

        # Log
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(80)
        self._log.setText("[通知通道状态] 邮件: 正常 | 企业微信: 正常 | 钉钉: 未配置 | 短信: 未配置")
        layout.addWidget(self._log)

    def _test_notify(self):
        ch = self._channel_combo.currentText()
        show_success(self, "测试通知", f"已向 {ch} 发送测试消息\n请检查目标端是否收到")
        self._log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 测试通知已发送至 {ch}")

    def _save_config(self):
        self._log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 配置已保存")
        show_success(self, "保存成功", "通知通道配置已保存")

    def _new_rule(self):
        show_info(self, "新建通知规则", "规则名称:\n告警级别:\n通知通道:\n静默周期:")

    def _edit_rule(self):
        show_info(self, "编辑规则", "编辑表单已打开")

    def _toggle_rule(self):
        show_info(self, "切换状态", "规则已启用/禁用")

    def _del_rule(self):
        show_info(self, "删除规则", "规则已删除")
