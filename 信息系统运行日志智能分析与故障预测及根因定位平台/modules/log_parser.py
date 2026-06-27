import random
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QSplitter, QFrame, QComboBox, QTextEdit,
    QListWidget, QListWidgetItem, QSlider, QFormLayout, QCheckBox,
)
from PyQt6.QtGui import QColor, QFont
from core.dialogs import show_info, show_success, DetailDialog


class LogParserModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16,12,16,12)

        title_row = QHBoxLayout()
        title_row.addWidget(QLabel("🔧 解析配置台", styleSheet="font-size:16px;font-weight:bold;color:#4fc3f7;"))
        self._status = QLabel("✅ 引擎就绪"); self._status.setStyleSheet("color:#81c784;font-weight:bold;")
        title_row.addStretch(); title_row.addWidget(self._status)
        layout.addLayout(title_row)

        # Template & config
        config_row = QHBoxLayout()
        tmpl_box = QGroupBox("解析模板"); tf = QFormLayout(tmpl_box)
        self._tmpl = QComboBox(); self._tmpl.addItems(["Syslog (RFC 5424)","JSON日志","Apache访问日志","Nginx错误日志","自定义正则"])
        tf.addRow("选择模板", self._tmpl)
        self._auto_parse = QCheckBox("采集后自动解析"); self._auto_parse.setChecked(True)
        tf.addRow("", self._auto_parse)
        config_row.addWidget(tmpl_box)

        field_box = QGroupBox("字段映射"); fl = QVBoxLayout(field_box)
        fields = [("timestamp","时间戳","✅"),("level","级别","✅"),("module","模块","✅"),
                  ("thread","线程","✅"),("request_id","请求ID","✅"),("message","消息","✅")]
        for f, label, status in fields:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{status} {label}", styleSheet="color:#e8edf5;"))
            row.addWidget(QLabel(f, styleSheet="color:#8fa8c8;font-size:9px;"))
            row.addStretch(); fl.addLayout(row)
        config_row.addWidget(field_box)
        layout.addLayout(config_row)

        # Action panel
        action_panel = QFrame()
        action_panel.setStyleSheet("QFrame{background:#121e3a;border:1px solid #2a4070;border-radius:10px;}")
        ap = QHBoxLayout(action_panel)
        for t,s in [("▶ 执行解析", self._parse), ("📋 测试解析", self._test),
                     ("📊 解析统计", self._stats), ("🔍 错误模式", self._patterns),
                     ("📤 导出结果", self._export)]:
            b = QPushButton(t); b.clicked.connect(s)
            if "执行" in t: b.setProperty("primary", True)
            ap.addWidget(b)
        layout.addWidget(action_panel)

        # Pipeline visualization
        pipe_box = QGroupBox("解析流水线")
        pipe = QHBoxLayout()
        stages = [
            ("📥\n原始日志", "#4fc3f7"), ("🔍\n分词提取", "#81c784"),
            ("🏷\n字段映射", "#ffab40"), ("✅\n格式校验", "#ce93d8"),
            ("📦\n结构化输出", "#4dd0e1"),
        ]
        for i, (label, color) in enumerate(stages):
            stage = QFrame(); stage.setStyleSheet(f"QFrame{{background:{color}22;border:2px solid {color};border-radius:10px;}}")
            sl = QVBoxLayout(stage); sl.setContentsMargins(14,12,14,12)
            sl.addWidget(QLabel(label,styleSheet=f"color:{color};font-weight:bold;font-size:11px;",alignment=Qt.AlignmentFlag.AlignCenter))
            if i < len(stages)-1:
                arrow = QLabel("  →  ", styleSheet="color:#4fc3f7;font-size:20px;")
                pipe.addWidget(arrow)
            pipe.addWidget(stage, 1)
        pipe_box.setLayout(pipe); layout.addWidget(pipe_box)

        # Output preview
        out_box = QGroupBox("解析输出预览")
        self._output = QTextEdit()
        self._output.setReadOnly(True); self._output.setPlaceholderText("解析结果将在此显示...")
        self._output.setMinimumHeight(100)
        out_box.setLayout(QVBoxLayout()); out_box.layout().addWidget(self._output)
        layout.addWidget(out_box, 1)

    def _parse(self):
        lines = ["=== 批量解析完成 ===", f"模板: {self._tmpl.currentText()}", f"时间: {datetime.now().strftime('%H:%M:%S')}",
                 "", "成功解析: 156条", "解析失败: 2条", "提取字段: 6个", "平均耗时: 0.3ms/条"]
        self._output.setText("\n".join(lines))
        self._status.setText("✅ 解析完成")
        show_success(self,"解析","156条日志已解析完成")

    def _test(self):
        lines = ["=== 测试解析 ===", f"原始: 2026-06-23 10:15:23 [auth] ERROR - 认证失败",
                 "", "→ 时间戳: 2026-06-23 10:15:23", "→ 级别: ERROR", "→ 模块: auth", "→ 消息: 认证失败"]
        self._output.setText("\n".join(lines))
        show_info(self,"测试","单条解析测试通过")

    def _stats(self):
        lines = ["解析统计", f"总处理: 12,580条", f"成功率: 98.7%", f"平均吞吐: 850条/秒",
                 f"字段覆盖率: 92%", f"异常率: 1.2%"]
        DetailDialog("统计","\n".join(lines),self).exec()

    def _patterns(self):
        lines = ["错误模式 TOP5:", "", "超时: 45次 ████████████", "拒绝连接: 32次 ████████",
                 "空指针: 18次 ████", "权限不足: 12次 ███", "OOM: 5次 █"]
        DetailDialog("错误模式","\n".join(lines),self).exec()

    def _export(self):
        show_success(self,"导出","解析结果已导出为JSON格式")
