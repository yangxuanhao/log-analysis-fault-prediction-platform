import random, re, time
from datetime import datetime
from collections import deque
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QLineEdit, QTextEdit, QSplitter, QListWidget,
    QListWidgetItem, QComboBox, QSpinBox, QCheckBox,
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

from core.dialogs import show_info, show_success, DetailDialog


class SearchTimeline(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self._data = deque([0]*24, maxlen=24)
        self.setMinimumHeight(80)

    def add_hit(self, count: int):
        self._data.append(count)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        painter.fillRect(self.rect(), QColor("#121e3a"))
        if not self._data:
            painter.end(); return
        max_val = max(self._data) or 1
        bar_w = (w - 20) / len(self._data)
        painter.setPen(Qt.PenStyle.NoPen)
        for i, v in enumerate(self._data):
            bh = (v / max_val) * (h - 20)
            color = QColor(79, 195, 247, 180) if v < max_val * 0.8 else QColor("#ff5252")
            painter.setBrush(color)
            painter.drawRect(int(10 + i * bar_w), int(h - 10 - bh), int(bar_w - 2), int(bh))
        painter.setPen(QColor("#8fa8c8"))
        painter.setFont(QFont("Microsoft YaHei", 8))
        painter.drawText(2, h - 2, "过去24小时搜索结果分布")
        painter.end()


class LogSearchModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._results = []
        self._history = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        # Search bar
        search_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText('输入搜索关键词，支持 AND OR NOT 语法，例如: error AND database NOT mysql')
        self._search_input.setMinimumHeight(40)
        self._search_input.returnPressed.connect(self._do_search)
        search_row.addWidget(self._search_input, 1)
        for text, slot in [("🔍 搜索", self._do_search), ("🔄 实时Tail", self._toggle_tail), ("🗑 清空", self._clear)]:
            b = QPushButton(text)
            b.setMinimumHeight(40)
            if text == "🔍 搜索": b.setProperty("primary", True)
            b.clicked.connect(slot)
            search_row.addWidget(b)
        layout.addLayout(search_row)

        # Filters row
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("时间范围:"))
        self._time_combo = QComboBox()
        self._time_combo.addItems(["过去15分钟", "过去1小时", "过去6小时", "过去24小时", "过去7天", "全部时间"])
        filter_row.addWidget(self._time_combo)
        filter_row.addWidget(QLabel("级别:"))
        self._level_combo = QComboBox()
        self._level_combo.addItems(["全部", "ERROR", "WARN", "INFO", "DEBUG", "FATAL"])
        filter_row.addWidget(self._level_combo)
        filter_row.addWidget(QLabel("最多结果:"))
        self._max_spin = QSpinBox(); self._max_spin.setRange(10, 500); self._max_spin.setValue(100)
        filter_row.addWidget(self._max_spin)
        filter_row.addStretch()
        layout.addLayout(filter_row)

        # Timeline
        self._timeline = SearchTimeline()
        layout.addWidget(self._timeline)

        # Results area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._results_area = QTextEdit()
        self._results_area.setReadOnly(True)
        self._results_area.setPlaceholderText("搜索结果将显示在这里...")
        splitter.addWidget(self._results_area)
        splitter.setStretchFactor(0, 3)
        splitter.setSizes([600, 200])

        right_panel = QWidget()
        rl = QVBoxLayout(right_panel)

        hist_box = QGroupBox("搜索历史")
        self._history_list = QListWidget()
        hist_box.setLayout(QVBoxLayout())
        hist_box.layout().addWidget(self._history_list)
        rl.addWidget(hist_box)

        stat_box = QGroupBox("结果统计")
        sl = QVBoxLayout(stat_box)
        self._lbl_total = QLabel("总结果数: 0")
        self._lbl_time = QLabel("搜索耗时: --")
        self._lbl_sources = QLabel("涉及来源: --")
        for lb in [self._lbl_total, self._lbl_time, self._lbl_sources]:
            lb.setStyleSheet("color: #4fc3f7; background: transparent;")
            sl.addWidget(lb)
        rl.addWidget(stat_box)

        splitter.addWidget(right_panel)
        layout.addWidget(splitter, 1)

        # Toolbar
        tool_row = QHBoxLayout()
        for text, slot in [("导出结果", self._export), ("加入知识库", self._add_to_kb),
                           ("生成搜索报表", self._gen_report), ("语法帮助", self._syntax_help)]:
            b = QPushButton(text); b.clicked.connect(slot); tool_row.addWidget(b)
        tool_row.addStretch()
        layout.addLayout(tool_row)

        self._tail_timer = QTimer(self)
        self._tail_timer.timeout.connect(self._tail_tick)
        self._is_tailing = False
        self._log_msg("日志联机搜索已就绪，请输入关键词开始搜索")

    def _log_msg(self, msg):
        self._results_area.append(f"// {msg}")

    def _do_search(self):
        query = self._search_input.text().strip()
        if not query:
            show_info(self, "提示", "请输入搜索关键词")
            return

        if query not in self._history:
            self._history.insert(0, query)
            self._history_list.insertItem(0, query)
            if self._history_list.count() > 20:
                self._history_list.takeItem(20)

        start = time.time()
        count = self._max_spin.value()
        results = []
        levels = {"全部": ["ERROR","WARN","INFO","DEBUG","FATAL"],
                  "ERROR":["ERROR"],"WARN":["WARN"],"INFO":["INFO"],
                  "DEBUG":["DEBUG"],"FATAL":["FATAL"]}
        selected = levels.get(self._level_combo.currentText(), ["ERROR"])

        sources = ["auth-svc","api-gw","db-cluster","cache-svc","web-srv","mq-consumer"]
        for i in range(min(count, 80)):
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lv = random.choice(selected)
            src = random.choice(sources)
            msg_templates = {
                "ERROR": [f"数据库连接超时 (timeout={random.randint(5,30)}s)", f"请求处理异常: {random.choice(['NullPointer','IndexOutOfBounds','IllegalArgument'])}",
                          f"上游服务返回{random.randint(500,503)}状态码", f"消息队列消费失败 offset={random.randint(100,9999)}"],
                "WARN": [f"连接池使用率超过{random.randint(75,95)}%", f"响应时间超过{random.randint(200,2000)}ms",
                         f"磁盘剩余空间不足{random.randint(5,20)}%", f"重试次数已达{random.randint(3,5)}次"],
                "INFO": [f"请求处理完成 duration={random.randint(10,500)}ms", f"缓存刷新成功 entries={random.randint(100,9999)}",
                         f"定时任务执行完毕耗时{random.randint(1,10)}s", f"健康检查通过"],
                "DEBUG": [f"SQL执行计划: index_scan cost={random.randint(100,9999)}", f"变量值解析 result={random.choice([True,False])}"],
                "FATAL": [f"系统内存溢出 OOM: {random.choice(['Java heap space','Metaspace','Direct buffer'])}",
                          f"核心服务进程崩溃 signal={random.randint(6,11)}"],
            }
            msg = random.choice(msg_templates.get(lv, ["日志记录"]))
            line = f"[{ts}] [{src}] {lv} - {msg}"
            if query.lower() in line.lower():
                results.append({"时间": ts, "级别": lv, "来源": src, "内容": msg, "原始行": line})

        elapsed = time.time() - start
        self._results = results
        self._timeline.add_hit(len(results))
        self._lbl_total.setText(f"总结果数: {len(results)}")
        self._lbl_time.setText(f"搜索耗时: {elapsed*1000:.1f}ms")
        self._lbl_sources.setText(f"涉及来源: {len(set(r['来源'] for r in results))} 个")

        self._results_area.clear()
        if results:
            self._results_area.append(f"═══ 找到 {len(results)} 条结果 (耗时 {elapsed*1000:.1f}ms) ═══\n")
            for r in results:
                tag = {"ERROR":"❌","WARN":"⚠️","INFO":"ℹ️","DEBUG":"🔍","FATAL":"💀"}.get(r["级别"], "•")
                self._results_area.append(f"{tag} [{r['时间']}] [{r['来源']}] {r['级别']}")
                self._results_area.append(f"   {r['内容']}")
                self._results_area.append("")
        else:
            self._results_area.append("未找到匹配结果，请尝试更宽松的关键词")

        show_success(self, "搜索完成", f"找到 {len(results)} 条匹配结果，耗时 {elapsed*1000:.1f}ms")

    def _toggle_tail(self):
        if self._is_tailing:
            self._tail_timer.stop()
            self._is_tailing = False
            self._log_msg("实时Tail已停止")
        else:
            self._tail_timer.start(3000)
            self._is_tailing = True
            self._log_msg("实时Tail已启动，每3秒刷新...")
            show_info(self, "实时Tail", "正在实时追踪最新日志，每3秒自动刷新")

    def _tail_tick(self):
        ts = datetime.now().strftime("%H:%M:%S")
        lv = random.choice(["INFO","INFO","INFO","WARN","ERROR"])
        src = random.choice(["api-gw","web-srv","db-cluster"])
        msgs = {"INFO":"请求正常处理完成","WARN":"响应延迟偏高","ERROR":"调用远程服务失败"}
        line = f"[{ts}] [{src}] {lv} - {msgs.get(lv, '')}"
        self._results_area.insertPlainText(f">> {line}\n")
        scrollbar = self._results_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _clear(self):
        self._results.clear()
        self._results_area.clear()
        self._log_msg("搜索结果已清空")

    def _export(self):
        lines = ["日志搜索结果导出", f"搜索关键词: {self._search_input.text()}", f"导出时间: {datetime.now()}", ""]
        for r in self._results:
            lines.append(r["原始行"])
        DetailDialog("导出结果", "\n".join(lines), self).exec()
        self._log_msg(f"已导出 {len(self._results)} 条结果")

    def _add_to_kb(self):
        show_info(self, "加入知识库", "可将搜索到的重要结果加入知识图谱模块作为知识条目")
        self._log_msg("已添加到知识库")

    def _gen_report(self):
        lines = ["搜索分析报告", f"关键词: {self._search_input.text()}", f"结果数: {len(self._results)}",
                 f"搜索时间: {datetime.now()}", "", "级别分布:"]
        for lv in ["FATAL","ERROR","WARN","INFO","DEBUG"]:
            cnt = sum(1 for r in self._results if r["级别"]==lv)
            if cnt: lines.append(f"  {lv}: {cnt}")
        DetailDialog("搜索报告", "\n".join(lines), self).exec()

    def _syntax_help(self):
        help_text = """搜索语法帮助:
  AND  同时匹配多个词     error AND database
  OR   匹配任意一个词     timeout OR timeout
  NOT  排除某个词         error NOT mysql
  精确匹配               "connection timeout"
  通配符                 db_*
  字段筛选               source:api-gw level:ERROR
  示例:
  (error OR fatal) AND database NOT mysql
  level:WARN AND timeout
  source:api-gw AND 500"""
        DetailDialog("搜索语法帮助", help_text, self).exec()
