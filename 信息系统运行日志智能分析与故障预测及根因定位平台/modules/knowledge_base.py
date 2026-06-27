from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QSplitter, QFrame, QTextEdit, QLineEdit,
    QComboBox, QSlider, QFormLayout, QProgressBar,
)
from PyQt6.QtGui import QColor, QFont
from core.dialogs import show_info, show_success, DetailDialog


class KnowledgeBaseModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16,12,16,12)

        title_row = QHBoxLayout()
        title_row.addWidget(QLabel("🧠 知识工坊", styleSheet="font-size:16px;font-weight:bold;color:#4fc3f7;"))
        title_row.addStretch()
        layout.addLayout(title_row)

        # Search & match area
        search_panel = QFrame(); search_panel.setStyleSheet("QFrame{background:#121e3a;border:1px solid #2a4070;border-radius:10px;}")
        sp = QVBoxLayout(search_panel); sp.setContentsMargins(16,14,16,14)
        sp.addWidget(QLabel("智能检索", styleSheet="color:#4fc3f7;font-weight:bold;font-size:13px;"))
        sr = QHBoxLayout()
        self._search_input = QLineEdit(); self._search_input.setPlaceholderText("输入故障症状描述...")
        sr.addWidget(self._search_input, 1)
        self._tag_cb = QComboBox(); self._tag_cb.addItems(["全部分类","数据库","JVM","磁盘","网络","缓存","服务"])
        sr.addWidget(self._tag_cb)
        sp.addLayout(sr)

        match_row = QHBoxLayout()
        self._match_progress = QProgressBar(); self._match_progress.setRange(0,100); self._match_progress.setValue(0)
        self._match_progress.setFormat("匹配度 %p%")
        match_row.addWidget(self._match_progress, 1)
        sp.addLayout(match_row)
        layout.addWidget(search_panel)

        # Case cards
        cases_row = QHBoxLayout()
        cases = [
            ("数据库连接超时", "连接池耗尽导致", "⭐ 95%", "#ff5252"),
            ("内存溢出OOM", "堆内存不足+泄漏", "⭐ 92%", "#ffab40"),
            ("磁盘写满", "日志未轮转归档", "⭐ 98%", "#81c784"),
            ("缓存雪崩", "大量缓存同时过期", "⭐ 90%", "#4fc3f7"),
        ]
        for title, desc, conf, color in cases:
            card = QFrame(); card.setStyleSheet(f"QFrame{{background:{color}15;border:2px solid {color};border-radius:10px;}}")
            cl = QVBoxLayout(card); cl.setContentsMargins(12,10,12,10)
            cl.addWidget(QLabel(title,styleSheet="color:#e8edf5;font-weight:bold;font-size:12px;"))
            cl.addWidget(QLabel(desc,styleSheet="color:#8fa8c8;font-size:10px;"))
            cl.addWidget(QLabel(conf,styleSheet="color:#ffd740;font-size:14px;"))
            cases_row.addWidget(card, 1)
        layout.addLayout(cases_row)

        # Knowledge tools
        tools_panel = QFrame(); tools_panel.setStyleSheet("QFrame{background:#121e3a;border:1px solid #2a4070;border-radius:10px;}")
        tp = QHBoxLayout(tools_panel)
        for t, s, c in [("🔍 相似度匹配", self._match, True), ("📚 案例学习", self._learn, False),
                        ("➕ 新建案例", self._add, False), ("📤 导出库", self._export, False),
                        ("🔄 重新索引", self._reindex, False)]:
            b = QPushButton(t); b.clicked.connect(s)
            if c: b.setProperty("primary", True)
            tp.addWidget(b)
        layout.addWidget(tools_panel)

        # Detail
        detail_box = QGroupBox("案例详情预览")
        self._detail = QTextEdit()
        self._detail.setReadOnly(True); self._detail.setPlaceholderText("点击「案例学习」获取推荐案例...")
        detail_box.setLayout(QVBoxLayout()); detail_box.layout().addWidget(self._detail)
        layout.addWidget(detail_box, 1)

        self._log = QTextEdit(); self._log.setReadOnly(True); self._log.setMaximumHeight(60)
        self._log.setText("[就绪] 知识库加载完成 6个案例")
        layout.addWidget(self._log)

    def _match(self):
        kw = self._search_input.text().strip() or "数据库连接失败"
        sim = len(kw) * 3
        self._match_progress.setValue(min(98, sim))
        self._detail.setText(f"🔍 匹配结果\n\n输入: {kw}\n\n最佳匹配: 数据库连接超时 (95%)\n根因: 连接池耗尽导致新连接被拒绝\n方案: 增加连接池大小至200\n\n相似案例: 服务无响应 (72%)\n         缓存雪崩 (65%)")
        self._log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 相似度匹配完成")

    def _learn(self):
        self._detail.setText("📖 推荐学习\n\n1. 数据库连接超时\n   根因: 连接池耗尽\n   方案: 优化连接池配置\n\n2. 内存溢出OOM\n   根因: 堆内存不足\n   方案: 调整JVM参数\n\n3. 缓存雪崩\n   根因: 同时过期\n   方案: 过期时间加随机偏移")
        show_info(self,"学习","推荐3个案例供学习")

    def _add(self):
        show_success(self,"新建","案例已添加，等待审核")
        self._log.append("[新增] 案例已提交审核")

    def _export(self):
        lines = ["知识库导出", "条目: 6个", "格式: JSON", f"时间: {datetime.now().strftime('%Y-%m-%d')}"]
        DetailDialog("导出","\n".join(lines),self).exec()

    def _reindex(self):
        self._match_progress.setValue(0)
        self._match_progress.setStyleSheet("")
        from PyQt6.QtCore import QTimer
        self._idx_timer = QTimer(self)
        self._idx_timer._v = 0
        def step():
            self._idx_timer._v += 5
            self._match_progress.setValue(self._idx_timer._v)
            if self._idx_timer._v >= 100:
                self._idx_timer.stop()
                self._log.append("[索引] 重建完成 6/6 条")
                show_success(self,"索引","知识库索引重建完成")
        self._idx_timer.timeout.connect(step)
        self._idx_timer.start(50)
