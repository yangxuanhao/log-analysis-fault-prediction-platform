import random
import math
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QGridLayout, QProgressBar, QTextEdit, QFrame,
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient

from core.dialogs import show_info, show_success, DetailDialog


class HealthRadar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._metrics = {"日志采集": 0.92, "解析引擎": 0.88, "异常检测": 0.85,
                         "故障预测": 0.78, "根因定位": 0.82, "告警管理": 0.90}
        self._pulse = 0.0
        self.setMinimumSize(260, 260)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)

    def _tick(self) -> None:
        self._pulse += 0.02
        for k in self._metrics:
            self._metrics[k] = max(0.5, min(1.0, self._metrics[k] + random.uniform(-0.01, 0.01)))
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        r = min(w, h) * 0.35

        painter.setPen(QPen(QColor("#2a4070"), 1))
        for i in range(3):
            painter.drawEllipse(QRectF(cx - r * (i+1)/3, cy - r * (i+1)/3, r * 2*(i+1)/3, r * 2*(i+1)/3))

        angles = list(self._metrics.values())
        names = list(self._metrics.keys())
        n = len(angles)
        points = []
        for i in range(n):
            a = math.pi * 2 * i / n - math.pi / 2
            val = angles[i]
            px = cx + r * val * math.cos(a)
            py = cy + r * val * math.sin(a)
            points.append((px, py))

        painter.setPen(QPen(QColor(79, 195, 247, 80), 1))
        for i in range(n):
            painter.drawLine(cx, cy, int(points[i][0]), int(points[i][1]))

        alpha = int(60 + 30 * math.sin(self._pulse))
        painter.setBrush(QColor(79, 195, 247, alpha))
        painter.setPen(QPen(QColor("#4fc3f7"), 2))
        for i in range(n):
            p1 = points[i]
            p2 = points[(i + 1) % n]
            painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
        for px, py in points:
            painter.drawEllipse(int(px) - 4, int(py) - 4, 8, 8)

        painter.setPen(QColor("#8fa8c8"))
        painter.setFont(QFont("Microsoft YaHei UI", 8))
        for i, name in enumerate(names):
            a = math.pi * 2 * i / n - math.pi / 2
            lx = cx + r * 1.15 * math.cos(a)
            ly = cy + r * 1.15 * math.sin(a)
            painter.drawText(QRectF(int(lx) - 40, int(ly) - 8, 80, 16), Qt.AlignmentFlag.AlignCenter, name)

        painter.setPen(QPen(QColor(79, 195, 247, 30)))
        pulse_angle = self._pulse % (math.pi * 2)
        painter.drawLine(cx, cy, int(cx + r * math.cos(pulse_angle)), int(cy + r * math.sin(pulse_angle)))
        painter.end()


class DashboardModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_metrics)
        self._timer.start(3000)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        top = QHBoxLayout()
        self._radar = HealthRadar()
        top.addWidget(self._radar)

        kpi_grid = QGridLayout()
        kpis = [
            ("日志处理量", "125,680 条/小时", 85), ("异常检出率", "96.2%", 96),
            ("故障预测准确率", "92.5%", 93), ("告警收敛比", "8:1", 88),
            ("MTTR", "12.5 分钟", 75), ("系统可用率", "99.92%", 99),
            ("在线节点数", "128/128", 100), ("根因定位准确率", "87.3%", 87),
        ]
        for i, (name, value, pct) in enumerate(kpis):
            card = QFrame()
            card.setStyleSheet("QFrame { background: #121e3a; border: 1px solid #2a4070; border-radius: 8px; }")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(12, 10, 12, 10)
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet("color: #8fa8c8; background: transparent; font-size: 11px;")
            lbl_val = QLabel(value)
            lbl_val.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
            lbl_val.setStyleSheet("color: #4fc3f7; background: transparent;")
            cl.addWidget(lbl_name)
            cl.addWidget(lbl_val)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(pct)
            bar.setTextVisible(False)
            bar.setFixedHeight(6)
            cl.addWidget(bar)
            kpi_grid.addWidget(card, i // 4, i % 4)
        top.addLayout(kpi_grid, 2)
        layout.addLayout(top)

        mid = QHBoxLayout()
        alert_box = QGroupBox("系统运行概览")
        alert_lay = QVBoxLayout(alert_box)
        self._overview = QTextEdit()
        self._overview.setReadOnly(True)
        self._overview.setMaximumHeight(120)
        self._overview.setText(
            "系统状态: 正常运行 ✅\n"
            "日志采集速率: 1,250 条/秒\n"
            "最新异常: 数据库连接池告警 (P1)\n"
            "上次故障: 12分钟前 (已自动恢复)"
        )
        alert_lay.addWidget(self._overview)
        mid.addWidget(alert_box, 2)

        status_frame = QFrame()
        status_frame.setFixedWidth(240)
        sl = QVBoxLayout(status_frame)
        self._lbl_mode = QLabel("运行模式: 自动巡检")
        self._lbl_health = QLabel("综合健康度: 92%")
        self._lbl_alerts = QLabel("当前告警: 3 条")
        for lb in [self._lbl_mode, self._lbl_health, self._lbl_alerts]:
            lb.setStyleSheet("color: #4fc3f7; background: transparent; font-size: 12px;")
            sl.addWidget(lb)
        sl.addStretch()
        mid.addWidget(status_frame)
        layout.addLayout(mid)

        for buttons in [
            [("刷新态势", self._refresh_view), ("健康检查", self._health_check),
             ("性能快照", self._snapshot), ("导出状态", self._export_status)],
            [("系统自检", self._self_test), ("组件状态", self._component_status),
             ("流量监控", self._traffic_monitor), ("生成综合报告", self._gen_report)],
        ]:
            r = QHBoxLayout()
            for text, slot in buttons:
                b = QPushButton(text)
                if text == "刷新态势":
                    b.setProperty("primary", True)
                b.clicked.connect(slot)
                r.addWidget(b)
            layout.addLayout(r)

    def _refresh_view(self) -> None:
        self._overview.setText(
            f"系统状态: 正常运行 ✅\n"
            f"日志采集速率: {random.randint(800, 2000)} 条/秒\n"
            f"最新异常: {'数据库连接池告警' if random.random() > 0.5 else '无新异常'}\n"
            f"综合健康度: {random.uniform(88, 99.5):.1f}%"
        )
        show_success(self, "已刷新", "态势感知面板已更新")

    def _health_check(self) -> None:
        checks = [("日志采集", True), ("解析引擎", True), ("异常检测", True),
                  ("故障预测", True), ("告警中心", True), ("数据库连接", True)]
        lines = ["系统健康检查结果:", ""]
        for name, ok in checks:
            icon = "✅" if ok and random.random() > 0.1 else "⚠️" if random.random() > 0.05 else "❌"
            lines.append(f"  {icon} {name}")
        DetailDialog("健康检查", "\n".join(lines), self).exec()

    def _snapshot(self) -> None:
        lines = [
            "系统性能快照",
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"CPU: {random.uniform(20, 80):.1f}%",
            f"内存: {random.uniform(40, 85):.1f}%",
            f"磁盘IO: {random.uniform(10, 200):.1f} MB/s",
            f"网络IO: {random.uniform(50, 500):.1f} Mbps",
            f"日志队列: {random.randint(0, 500)} 条积压",
        ]
        DetailDialog("性能快照", "\n".join(lines), self).exec()

    def _export_status(self) -> None:
        lines = [
            "系统状态报告",
            f"时间: {datetime.now()}",
            "运行模式: 自动巡检",
            f"综合健康度: {random.uniform(85, 99):.1f}%",
            "组件状态: 全部正常",
        ]
        DetailDialog("状态导出", "\n".join(lines), self).exec()

    def _self_test(self) -> None:
        lines = ["系统自检结果:", "",
                 "✅ 核心引擎自检通过",
                 "✅ 日志采集通路正常",
                 "✅ 告警通道连接正常",
                 "✅ 数据库连接正常",
                 "⚠️ 备份节点延迟偏高 (120ms)"]
        DetailDialog("系统自检", "\n".join(lines), self).exec()

    def _component_status(self) -> None:
        lines = ["组件运行状态:", "",
                 "🟢 日志采集器 - 运行中 (正常运行30d)",
                 "🟢 日志解析器 - 运行中 (吞吐量850条/s)",
                 "🟡 异常检测 - 运行中 (模型版本v2.3)",
                 "🟢 故障预测 - 运行中 (预测窗口15min)",
                 "🟢 根因分析 - 运行中 (知识库版本v5)",
                 "🔴 告警通知 - 异常 (微信通知通道中断)"]
        DetailDialog("组件状态", "\n".join(lines), self).exec()

    def _traffic_monitor(self) -> None:
        lines = ["流量监控面板:", "",
                 f"入站日志: {random.randint(500, 2000)} 条/秒",
                 f"解析输出: {random.randint(450, 1900)} 条/秒",
                 f"异常事件: {random.randint(0, 10)} 次/分",
                 f"告警流量: {random.randint(0, 5)} 条/分",
                 f"带宽占用: {random.uniform(10, 60):.1f} Mbps"]
        DetailDialog("流量监控", "\n".join(lines), self).exec()

    def _gen_report(self) -> None:
        lines = [
            "综合态势报告",
            f"时间: {datetime.now()}",
            "",
            "【系统概况】",
            "运行时长: 15天8小时",
            "总日志处理: 18,250,000 条",
            "异常检出: 1,285 次",
            "故障预测: 47 次 (准确率92.5%)",
            "MTTR: 12.5 分钟",
            "",
            "【健康评分】",
            "日志采集: 98%",
            "解析引擎: 95%",
            "异常检测: 92%",
            "根因定位: 88%",
            "综合评分: 93%",
        ]
        DetailDialog("综合报告", "\n".join(lines), self).exec()

    def _update_metrics(self) -> None:
        self._lbl_health.setText(f"综合健康度: {random.uniform(88, 98):.1f}%")
        self._lbl_alerts.setText(f"当前告警: {random.randint(0, 8)} 条")
