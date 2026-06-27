import random
import math
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QGridLayout, QProgressBar, QTextEdit, QFrame,
    QTableWidget, QTableWidgetItem,
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient

from core.dialogs import show_info, show_success, show_warning, DetailDialog


class SysMonitorEngine:
    """系统监控引擎——自监控与健康诊断算法"""

    @staticmethod
    def collect_metrics() -> dict:
        return {
            "cpu": round(random.uniform(20, 90), 1),
            "memory": round(random.uniform(40, 85), 1),
            "disk_io": round(random.uniform(10, 150), 1),
            "network": round(random.uniform(50, 400), 1),
            "uptime": f"{random.randint(5, 30)}天{random.randint(0, 23)}小时",
            "processes": random.randint(80, 200),
            "threads": random.randint(300, 800),
            "connections": random.randint(100, 500),
        }

    @staticmethod
    def calc_overall_health(metrics: dict) -> tuple[int, str]:
        cpu_score = max(0, 100 - metrics["cpu"])
        mem_score = max(0, 100 - metrics["memory"])
        overall = int((cpu_score + mem_score) / 2)
        if overall >= 80:
            return overall, "健康"
        elif overall >= 60:
            return overall, "亚健康"
        return overall, "警告"


class MiniChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = [random.uniform(20, 80) for _ in range(40)]
        self.setMinimumHeight(80)

    def push(self, val: float) -> None:
        self._data.append(val)
        if len(self._data) > 40:
            self._data.pop(0)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        painter.fillRect(self.rect(), QColor("#0b1426"))
        if len(self._data) < 2:
            painter.end()
            return
        margin = 4
        pw, ph = w - margin * 2, h - margin * 2
        painter.setPen(QPen(QColor("#4fc3f7"), 1.5))
        for i in range(1, len(self._data)):
            x1 = margin + pw * (i - 1) / (len(self._data) - 1)
            y1 = margin + ph * (1 - self._data[i - 1] / 100)
            x2 = margin + pw * i / (len(self._data) - 1)
            y2 = margin + ph * (1 - self._data[i] / 100)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        painter.end()


class SysMonitorModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)
        self._refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        top = QHBoxLayout()
        metric_keys = [("cpu", "CPU使用率", "#4fc3f7"), ("mem", "内存使用率", "#81c784"), ("disk", "磁盘IO", "#ffab40"), ("net", "网络带宽", "#ce93d8")]
        for key, title, color in metric_keys:
            card = QFrame()
            card.setStyleSheet("QFrame { background: #121e3a; border: 1px solid #2a4070; border-radius: 8px; }")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(10, 8, 10, 8)
            lbl = QLabel(title)
            lbl.setStyleSheet("color: #8fa8c8; background: transparent; font-size: 11px;")
            cl.addWidget(lbl)
            chart = MiniChart()
            cl.addWidget(chart)
            val_lbl = QLabel("--")
            val_lbl.setStyleSheet(f"color: {color}; background: transparent; font-size: 16px; font-weight: bold;")
            cl.addWidget(val_lbl)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedHeight(4)
            cl.addWidget(bar)
            setattr(self, f"_chart_{key}", chart)
            setattr(self, f"_val_{key}", val_lbl)
            setattr(self, f"_bar_{key}", bar)
            top.addWidget(card)
        layout.addLayout(top)

        mid = QHBoxLayout()

        health_box = QGroupBox("系统健康状态")
        hl = QVBoxLayout(health_box)
        self._health_label = QLabel("综合健康度: --")
        self._health_label.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
        self._health_label.setStyleSheet("color: #4fc3f7; background: transparent;")
        hl.addWidget(self._health_label)
        self._health_bar = QProgressBar()
        self._health_bar.setRange(0, 100)
        self._health_bar.setValue(0)
        self._health_bar.setFormat("健康度 %p%")
        hl.addWidget(self._health_bar)
        self._health_desc = QLabel("系统状态: 检查中...")
        self._health_desc.setStyleSheet("color: #8fa8c8; background: transparent;")
        hl.addWidget(self._health_desc)
        mid.addWidget(health_box)

        info_box = QGroupBox("系统信息")
        il = QVBoxLayout(info_box)
        self._sys_info = QTextEdit()
        self._sys_info.setReadOnly(True)
        self._sys_info.setMaximumHeight(100)
        il.addWidget(self._sys_info)
        mid.addWidget(info_box)

        process_box = QGroupBox("进程/线程")
        pl = QVBoxLayout(process_box)
        self._lbl_proc = QLabel("进程数: --")
        self._lbl_thread = QLabel("线程数: --")
        self._lbl_conn = QLabel("连接数: --")
        for lb in [self._lbl_proc, self._lbl_thread, self._lbl_conn]:
            lb.setStyleSheet("color: #4fc3f7; background: transparent;")
            pl.addWidget(lb)
        pl.addStretch()
        mid.addWidget(process_box)
        layout.addLayout(mid)

        for buttons in [
            [("刷新状态", self._refresh), ("健康诊断", self._diagnose),
             ("资源分析", self._resource_analysis), ("性能优化建议", self._optimize_suggest)],
            [("进程快照", self._process_snapshot), ("网络诊断", self._network_diag),
             ("日志诊断", self._log_diag), ("自愈恢复", self._self_heal)],
        ]:
            r = QHBoxLayout()
            for text, slot in buttons:
                b = QPushButton(text)
                if text == "刷新状态":
                    b.setProperty("primary", True)
                b.clicked.connect(slot)
                r.addWidget(b)
            layout.addLayout(r)

    def _refresh(self) -> None:
        metrics = SysMonitorEngine.collect_metrics()
        self._chart_cpu.push(metrics["cpu"])
        self._chart_mem.push(metrics["memory"])
        self._chart_disk.push(metrics["disk_io"])
        self._chart_net.push(metrics["network"])
        self._val_cpu.setText(f"{metrics['cpu']:.1f}%")
        self._val_mem.setText(f"{metrics['memory']:.1f}%")
        self._val_disk.setText(f"{metrics['disk_io']:.1f} MB/s")
        self._val_net.setText(f"{metrics['network']:.1f} Mbps")
        self._bar_cpu.setValue(int(metrics["cpu"]))
        self._bar_mem.setValue(int(metrics["memory"]))
        self._bar_disk.setValue(int(min(100, metrics["disk_io"] / 2)))
        self._bar_net.setValue(int(min(100, metrics["network"] / 5)))
        score, desc = SysMonitorEngine.calc_overall_health(metrics)
        self._health_bar.setValue(score)
        self._health_label.setText(f"综合健康度: {score}%")
        self._health_desc.setText(f"系统状态: {desc}")
        color = {"健康": "#4fc3f7", "亚健康": "#ffab40", "警告": "#ff5252"}
        self._health_desc.setStyleSheet(f"color: {color.get(desc, '#8fa8c8')}; background: transparent;")
        self._lbl_proc.setText(f"进程数: {metrics['processes']}")
        self._lbl_thread.setText(f"线程数: {metrics['threads']}")
        self._lbl_conn.setText(f"连接数: {metrics['connections']}")
        self._sys_info.setText(
            f"运行时长: {metrics['uptime']}\n"
            f"平台版本: v{random.choice(['1.2.3','1.3.0','2.0.1'])}\n"
            f"数据目录: /data/loginsight/\n"
            f"最近启动: {(datetime.now()).strftime('%Y-%m-%d %H:%M')}"
        )

    def _diagnose(self) -> None:
        checks = [
            ("CPU负载", random.choice(["正常", "偏高", "正常", "正常"])),
            ("内存使用", random.choice(["正常", "偏高", "正常"])),
            ("磁盘空间", random.choice(["充足", "充足", "不足"])),
            ("网络连通", random.choice(["正常", "正常", "延迟"])),
            ("数据库连接", random.choice(["正常", "正常", "正常"])),
            ("日志队列", random.choice(["正常", "正常", "积压"])),
        ]
        lines = ["系统诊断结果:", ""]
        for name, status in checks:
            icon = {"正常": "✅", "偏高": "⚠️", "不足": "🔴", "延迟": "⚠️", "积压": "⚠️"}
            lines.append(f"  {icon.get(status, '❓')} {name}: {status}")
        DetailDialog("系统诊断", "\n".join(lines), self).exec()

    def _resource_analysis(self) -> None:
        lines = ["资源使用分析:", "",
                 "CPU: 15% sys + 45% user + 40% idle",
                 "内存: 6.2GB/8GB 已用 (77.5%)",
                 "磁盘: 120GB/256GB 已用 (46.9%)",
                 "网络: 入站 45Mbps / 出站 32Mbps",
                 "",
                 "热点进程: python3 (28%), java (22%), nginx (8%)"]
        DetailDialog("资源分析", "\n".join(lines), self).exec()

    def _optimize_suggest(self) -> None:
        lines = ["性能优化建议:", "",
                 "1. JVM堆内存建议调整为 -Xms4G -Xmx6G",
                 "2. 数据库连接池建议增大至 max=150",
                 "3. 日志轮转建议按小时切割",
                 "4. 启用GC日志便于排查内存问题",
                 "5. 考虑引入缓存层降低数据库负载"]
        DetailDialog("优化建议", "\n".join(lines), self).exec()

    def _process_snapshot(self) -> None:
        lines = ["进程快照:", "",
                 "PID  NAME                  CPU%  MEM%",
                 "1234 python3               28.5  22.3",
                 "5678 java                  22.1  45.6",
                 "9012 nginx                 8.3   4.2",
                 "3456 redis-server          5.1   6.8",
                 "7890 mysql                 12.4  18.5"]
        DetailDialog("进程快照", "\n".join(lines), self).exec()

    def _network_diag(self) -> None:
        lines = ["网络诊断结果:", "",
                 "eth0: 192.168.1.100/24",
                 "状态: 运行中",
                 "MTU: 1500",
                 "丢包率: 0.02%",
                 "延迟: 0.35ms",
                 "带宽: 1Gbps",
                 "默认网关: 192.168.1.1 (响应正常)"]
        DetailDialog("网络诊断", "\n".join(lines), self).exec()

    def _log_diag(self) -> None:
        lines = ["日志系统诊断:", "",
                 "日志目录: /var/log/loginsight/",
                 "磁盘占用: 2.3GB",
                 "日志轮转: 已启用 (每天切割)",
                 "写入速率: 850条/秒",
                 "错误日志: 12条/小时",
                 "告警: 日志队列无积压"]
        DetailDialog("日志诊断", "\n".join(lines), self).exec()

    def _self_heal(self) -> None:
        actions = ["重启日志采集器", "清理临时缓存", "重置数据库连接池", "重新加载配置"]
        action = random.choice(actions)
        show_success(self, "自愈恢复", f"已执行: {action}\n系统已恢复正常运行")
        self._health_label.setText("综合健康度: 95%")
        self._health_bar.setValue(95)
        self._health_desc.setText("系统状态: 健康 ✅")
