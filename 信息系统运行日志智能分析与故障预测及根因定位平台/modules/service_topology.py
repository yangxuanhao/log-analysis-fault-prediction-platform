import random, math
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem,
)
from core.dialogs import show_info, show_success, show_warning, DetailDialog


class TopoCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(350)
        self._phase = 0.0
        self._nodes = [
            {"name": "负载均衡", "x": 0.5, "y": 0.08, "status": 1.0, "type": "lb"},
            {"name": "Web服务器", "x": 0.2, "y": 0.25, "status": 0.95, "type": "web"},
            {"name": "API网关", "x": 0.5, "y": 0.25, "status": 0.98, "type": "gw"},
            {"name": "Web服务器2", "x": 0.8, "y": 0.25, "status": 0.90, "type": "web"},
            {"name": "用户服务", "x": 0.1, "y": 0.5, "status": 0.92, "type": "svc"},
            {"name": "订单服务", "x": 0.35, "y": 0.5, "status": 0.85, "type": "svc"},
            {"name": "支付服务", "x": 0.6, "y": 0.5, "status": 0.78, "type": "svc"},
            {"name": "认证服务", "x": 0.85, "y": 0.5, "status": 0.95, "type": "svc"},
            {"name": "主数据库", "x": 0.25, "y": 0.75, "status": 0.88, "type": "db"},
            {"name": "缓存集群", "x": 0.55, "y": 0.75, "status": 0.92, "type": "cache"},
            {"name": "消息队列", "x": 0.8, "y": 0.75, "status": 0.96, "type": "mq"},
            {"name": "对象存储", "x": 0.5, "y": 0.92, "status": 0.99, "type": "storage"},
        ]
        self._edges = [(0,1),(0,2),(0,3),(2,4),(2,5),(2,6),(2,7),(4,8),(5,8),(6,9),(5,9),(7,8),(8,10),(9,10),(10,11)]
        self._timer = QTimer(self)
        self._timer.timeout.connect(lambda: setattr(self,'_phase',self._phase+0.03) or self.update())
        self._timer.start(40)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        painter.fillRect(self.rect(), QColor("#0a1628"))

        # Draw edges
        for i, j in self._edges:
            n1, n2 = self._nodes[i], self._nodes[j]
            x1, y1 = n1["x"]*w, n1["y"]*h
            x2, y2 = n2["x"]*w, n2["y"]*h
            status = (n1["status"] + n2["status"]) / 2
            alpha = int(80 + 120 * status)
            painter.setPen(QPen(QColor(79, 195, 247, alpha), 2))
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

            t = (self._phase * 0.5) % 1.0
            px = x1 + (x2-x1)*t; py = y1 + (y2-y1)*t
            painter.setBrush(QColor(129, 212, 250, 200))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(px, py), 4, 4)

        # Draw nodes
        for n in self._nodes:
            cx, cy = int(n["x"]*w), int(n["y"]*h)
            r = 24 if n["type"] in ("db","lb") else 20
            color_map = {"lb":"#4fc3f7","web":"#81c784","gw":"#ffab40","svc":"#ce93d8",
                         "db":"#ef5350","cache":"#ffd740","mq":"#4dd0e1","storage":"#8d6e63"}
            base_color = QColor(color_map.get(n["type"], "#666"))
            pulse = 0.7 + 0.3 * n["status"]
            painter.setBrush(QColor(base_color.red(), base_color.green(), base_color.blue(), int(180*pulse)))
            painter.setPen(QPen(base_color.lighter(130), 2))
            painter.drawEllipse(cx-r, cy-r, r*2, r*2)
            painter.setPen(QColor("#e8edf5"))
            painter.setFont(QFont("Microsoft YaHei", 8))
            painter.drawText(QRectF(cx-r-5, cy+8, r*2+10, 16), Qt.AlignmentFlag.AlignCenter, n["name"])
            painter.drawText(QRectF(cx-r-5, cy-12, r*2+10, 16), Qt.AlignmentFlag.AlignCenter, f"{n['status']*100:.0f}%")
        painter.end()


class ServiceTopologyModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._canvas = TopoCanvas()
        splitter.addWidget(self._canvas)
        splitter.setStretchFactor(0, 3)
        splitter.setSizes([600, 200])

        right = QWidget()
        rl = QVBoxLayout(right)

        info_box = QGroupBox("节点详情")
        self._detail_text = QTextEdit()
        self._detail_text.setReadOnly(True)
        self._detail_text.setPlaceholderText("点击拓扑图中的节点查看详情...")
        info_box.setLayout(QVBoxLayout())
        info_box.layout().addWidget(self._detail_text)
        rl.addWidget(info_box)

        tree_box = QGroupBox("依赖层级")
        self._dep_tree = QTreeWidget()
        self._dep_tree.setHeaderLabels(["服务组件", "状态"])
        self._build_tree()
        tree_box.setLayout(QVBoxLayout())
        tree_box.layout().addWidget(self._dep_tree)
        rl.addWidget(tree_box)

        splitter.addWidget(right)
        layout.addWidget(splitter, 1)

        for buttons in [
            [("自动发现拓扑", self._auto_discover), ("刷新状态", self._refresh_status),
             ("导出拓扑数据", self._export), ("拓扑分析", self._analyze)],
            [("放大(+)", self._zoom_in), ("缩小(-)", self._zoom_out),
             ("重置视图", self._reset_view), ("全屏展示", self._fullscreen)],
        ]:
            r = QHBoxLayout()
            for text, slot in buttons:
                b = QPushButton(text)
                if text == "自动发现拓扑": b.setProperty("primary", True)
                b.clicked.connect(slot)
                r.addWidget(b)
            layout.addLayout(r)

    def _build_tree(self):
        self._dep_tree.clear()
        layers = [
            ("入口层", [("负载均衡 (LB)", "🟢 正常")]),
            ("应用层", [("Web服务器集群", "🟢 正常"), ("API网关", "🟢 正常")]),
            ("服务层", [("用户服务", "🟢 正常"), ("订单服务", "🟡 延迟"), ("支付服务", "🔴 异常"), ("认证服务", "🟢 正常")]),
            ("数据层", [("主数据库", "🟡 连接池高"), ("缓存集群", "🟢 正常"), ("消息队列", "🟢 正常")]),
        ]
        for layer, items in layers:
            layer_item = QTreeWidgetItem(self._dep_tree, [layer, ""])
            for name, status in items:
                child = QTreeWidgetItem(layer_item, [name, status])
                if "🔴" in status: child.setForeground(1, QColor("#ff5252"))
                elif "🟡" in status: child.setForeground(1, QColor("#ffab40"))
            layer_item.setExpanded(True)

    def _auto_discover(self):
        self._detail_text.setText(f"[{datetime.now().strftime('%H:%M:%S')}] 拓扑自动发现完成\n\n发现 12 个服务节点\n检测到 15 条服务依赖关系\n服务健康度: 91.2%")
        show_success(self, "自动发现", "服务拓扑自动发现完成\n发现12个节点，15条依赖关系")

    def _refresh_status(self):
        for n in self._canvas._nodes:
            n["status"] = max(0.5, min(1.0, n["status"] + random.uniform(-0.05, 0.05)))
        self._canvas.update()
        self._detail_text.setText(f"[{datetime.now().strftime('%H:%M:%S')}] 状态已刷新")

    def _export(self):
        lines = ["服务拓扑数据", f"导出时间: {datetime.now()}", ""]
        for n in self._canvas._nodes:
            lines.append(f"{n['name']} (type={n['type']}) status={n['status']*100:.0f}%")
        DetailDialog("拓扑导出", "\n".join(lines), self).exec()

    def _analyze(self):
        unhealthy = [n for n in self._canvas._nodes if n["status"] < 0.8]
        lines = ["拓扑分析报告:", f"\n总节点数: {len(self._canvas._nodes)}",
                 f"异常节点: {len(unhealthy)}", f"平均健康度: {sum(n['status'] for n in self._canvas._nodes)/len(self._canvas._nodes)*100:.1f}%"]
        if unhealthy:
            lines.append("\n需关注节点:")
            for n in unhealthy: lines.append(f"  ⚠ {n['name']} ({n['status']*100:.0f}%)")
        DetailDialog("拓扑分析", "\n".join(lines), self).exec()

    def _zoom_in(self):
        self._detail_text.append("[缩放] 已放大")

    def _zoom_out(self):
        self._detail_text.append("[缩放] 已缩小")

    def _reset_view(self):
        self._detail_text.append("[视图] 已重置为默认视角")

    def _fullscreen(self):
        show_info(self, "全屏", "请使用窗口最大化按钮进入全屏展示模式")
