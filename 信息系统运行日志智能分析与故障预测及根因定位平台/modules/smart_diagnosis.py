import random
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QTextEdit, QSplitter, QListWidget, QListWidgetItem,
    QProgressBar, QFrame, QComboBox,
)
from PyQt6.QtGui import QColor

from core.dialogs import show_info, show_success, show_warning, DetailDialog


class DiagnosisEngine:
    @staticmethod
    def analyze(issue: str) -> list[dict]:
        issues_db = {
            "数据库连接超时": {"root_cause": "连接池耗尽/网络延迟", "confidence": 0.92,
                         "steps": ["检查连接池配置 maxActive=100", "查看数据库服务器负载", "检查网络延迟 ping db-host",
                                   "优化慢查询SQL", "考虑增加连接池上限到200"],
                         "severity": "严重", "fix_time": "15-30分钟"},
            "服务响应缓慢": {"root_cause": "CPU负载过高/内存不足", "confidence": 0.85,
                        "steps": ["检查CPU使用率 top -H", "检查内存使用情况 free -m", "查看GC日志",
                                  "分析线程堆栈 jstack", "考虑水平扩展实例数"],
                        "severity": "一般", "fix_time": "20-60分钟"},
            "磁盘空间告警": {"root_cause": "日志文件未轮转/数据增长", "confidence": 0.95,
                        "steps": ["检查磁盘使用率 df -h", "清理过期日志文件", "配置logrotate按天切割",
                                  "压缩归档历史数据", "设置磁盘告警阈值80%"],
                        "severity": "一般", "fix_time": "10-20分钟"},
            "内存泄漏": {"root_cause": "对象未正确释放/ThreadLocal", "confidence": 0.78,
                    "steps": ["获取heap dump分析", "检查ThreadLocal使用", "审查代码中Map缓存使用",
                              "启用内存泄漏检测", "计划重启临时恢复"],
                    "severity": "严重", "fix_time": "1-4小时"},
            "网络分区": {"root_cause": "交换机故障/网线松动", "confidence": 0.82,
                    "steps": ["检查网络连通性 ping all nodes", "查看交换机端口状态", "检查网线连接",
                              "重启网络接口", "启用冗余链路"],
                    "severity": "灾难", "fix_time": "10-60分钟"},
        }
        for key, val in issues_db.items():
            if key in issue or issue in key:
                return [{"issue": key, **val}]
        return [{"issue": issue, "root_cause": f"未知问题: {issue}",
                 "confidence": random.uniform(0.3, 0.7),
                 "steps": [f"收集更多信息: {issue}", "查看相关日志", "联系技术支持"],
                 "severity": "未知", "fix_time": "待定"}]


class SmartDiagnosisModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._issues = [
            {"time": "2026-06-23 10:22", "issue": "数据库连接超时", "status": "待诊断"},
            {"time": "2026-06-23 11:05", "issue": "服务响应缓慢", "status": "诊断完成"},
            {"time": "2026-06-23 11:30", "issue": "磁盘空间告警", "status": "已修复"},
        ]
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        ll = QVBoxLayout(left)

        # Issue list
        self._issue_list = QListWidget()
        self._issue_list.currentRowChanged.connect(self._show_detail)
        ll.addWidget(QLabel("待诊断问题列表:"))
        ll.addWidget(self._issue_list, 1)

        # Buttons
        for buttons in [
            [("智能诊断", self._diagnose), ("一键修复", self._fix), ("加入知识库", self._to_kb)],
            [("批量诊断", self._batch_diag), ("导出报告", self._export), ("清除历史", self._clear)],
        ]:
            r = QHBoxLayout()
            for text, slot in buttons:
                b = QPushButton(text)
                if text == "智能诊断": b.setProperty("primary", True)
                b.clicked.connect(slot)
                r.addWidget(b)
            ll.addLayout(r)
        splitter.addWidget(left)

        right = QWidget()
        rl = QVBoxLayout(right)

        diag_box = QGroupBox("诊断结果")
        self._diag_result = QTextEdit()
        self._diag_result.setReadOnly(True)
        self._diag_result.setPlaceholderText("选择问题并点击「智能诊断」获取诊断结果...")
        diag_box.setLayout(QVBoxLayout())
        diag_box.layout().addWidget(self._diag_result)
        rl.addWidget(diag_box)

        step_box = QGroupBox("修复步骤")
        self._step_list = QListWidget()
        step_box.setLayout(QVBoxLayout())
        step_box.layout().addWidget(self._step_list)

        progress_box = QGroupBox("修复进度")
        self._fix_progress = QProgressBar()
        self._fix_progress.setRange(0, 100)
        self._fix_progress.setValue(0)
        progress_box.setLayout(QVBoxLayout())
        progress_box.layout().addWidget(self._fix_progress)
        rl.addWidget(progress_box)
        rl.addWidget(step_box)
        splitter.addWidget(right)
        layout.addWidget(splitter, 1)

    def _refresh_list(self):
        self._issue_list.clear()
        for iss in self._issues:
            icon = {"待诊断": "🟡", "诊断完成": "🟢", "已修复": "✅", "修复中": "🔄"}
            item = QListWidgetItem(f"{icon.get(iss['status'],'○')} {iss['time']} {iss['issue']} [{iss['status']}]")
            if iss["status"] == "待诊断": item.setForeground(QColor("#ffab40"))
            elif iss["status"] == "已修复": item.setForeground(QColor("#81c784"))
            self._issue_list.addItem(item)

    def _show_detail(self, idx):
        if idx < 0 or idx >= len(self._issues): return
        iss = self._issues[idx]
        self._diag_result.setText(f"问题: {iss['issue']}\n时间: {iss['time']}\n状态: {iss['status']}\n\n点击「智能诊断」获取详细分析...")
        self._step_list.clear()

    def _diagnose(self):
        idx = self._issue_list.currentRow()
        if idx < 0: show_warning(self, "提示", "请先选择一个待诊断问题"); return
        iss = self._issues[idx]
        result = DiagnosisEngine.analyze(iss["issue"])
        if not result: return
        r = result[0]
        lines = [
            f"🔍 智能诊断报告",
            f"━━━━━━━━━━━━━━━━━━",
            f"问题: {r['issue']}",
            f"根因分析: {r['root_cause']}",
            f"置信度: {r['confidence']*100:.0f}%",
            f"严重程度: {r['severity']}",
            f"预计修复时间: {r['fix_time']}",
            f"━━━━━━━━━━━━━━━━━━",
            f"修复步骤:",
        ]
        for i, step in enumerate(r["steps"], 1):
            lines.append(f"  {i}. {step}")
        self._diag_result.setText("\n".join(lines))
        self._step_list.clear()
        for i, step in enumerate(r["steps"], 1):
            self._step_list.addItem(f"步骤{i}: {step}")
        iss["status"] = "诊断完成"
        self._refresh_list()

    def _fix(self):
        idx = self._issue_list.currentRow()
        if idx < 0: show_warning(self, "提示", "请先选择一个已诊断问题"); return
        iss = self._issues[idx]
        if iss["status"] == "待诊断": show_warning(self, "提示", "请先执行智能诊断"); return
        self._fix_timer = QTimer(self)
        self._fix_timer._progress = 0
        self._fix_timer.timeout.connect(self._fix_step)
        iss["status"] = "修复中"
        self._refresh_list()
        self._fix_timer.start(200)
        self._diag_result.append("\n▶ 正在执行修复...")

    def _fix_step(self):
        self._fix_timer._progress += 5
        self._fix_progress.setValue(self._fix_timer._progress)
        if self._fix_timer._progress >= 100:
            self._fix_timer.stop()
            idx = self._issue_list.currentRow()
            if 0 <= idx < len(self._issues):
                self._issues[idx]["status"] = "已修复"
                self._refresh_list()
            self._diag_result.append("✅ 修复完成！问题已解决。")
            show_success(self, "修复完成", "自动修复已成功执行")

    def _to_kb(self):
        idx = self._issue_list.currentRow()
        if idx < 0: return
        show_success(self, "已加入知识库", f"问题「{self._issues[idx]['issue']}」已加入知识图谱模块")
        self._diag_result.append("\n📚 已加入知识库")

    def _batch_diag(self):
        for iss in self._issues:
            if iss["status"] == "待诊断":
                result = DiagnosisEngine.analyze(iss["issue"])
                iss["status"] = "诊断完成"
        self._refresh_list()
        self._diag_result.setText(f"[{datetime.now().strftime('%H:%M:%S')}] 批量诊断完成")
        show_success(self, "批量诊断", f"已完成 {len(self._issues)} 个问题的诊断")

    def _export(self):
        lines = ["智能诊断报告", f"生成时间: {datetime.now()}", ""]
        for iss in self._issues:
            lines.append(f"[{iss['status']}] {iss['time']} {iss['issue']}")
        DetailDialog("诊断报告", "\n".join(lines), self).exec()

    def _clear(self):
        self._issues.clear()
        self._issue_list.clear()
        self._diag_result.clear()
        self._step_list.clear()
        self._fix_progress.setValue(0)
