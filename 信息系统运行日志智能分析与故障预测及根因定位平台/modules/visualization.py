import math
import random
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient,
    QFont, QPolygonF,
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QSlider, QComboBox, QCheckBox,
)

from core.dialogs import show_info, DetailDialog


def _iso(x: float, y: float, z: float, cx: float, cy: float, scale: float, rot: float) -> QPointF:
    cos_r = math.cos(math.radians(rot))
    sin_r = math.sin(math.radians(rot))
    xr = x * cos_r - z * sin_r
    zr = x * sin_r + z * cos_r
    sx = cx + (xr - zr) * scale * 0.866
    sy = cy + (xr + zr) * scale * 0.5 - y * scale
    return QPointF(sx, sy)


class TopoSceneCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(400)
        self._rot_y = -30.0
        self._rot_x = 20.0
        self._zoom = 1.0
        self._phase = 0.0
        self._flow = [random.uniform(0.3, 1.0) for _ in range(8)]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

    def _tick(self) -> None:
        self._phase += 0.04
        for i in range(len(self._flow)):
            self._flow[i] = 0.4 + 0.6 * abs(math.sin(self._phase + i * 0.7))
        self.update()

    def set_rotation(self, rx: float, ry: float) -> None:
        self._rot_x = rx
        self._rot_y = ry
        self.update()

    def set_zoom(self, z: float) -> None:
        self._zoom = max(0.4, min(2.5, (-z - 15) / 30.0))
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        bg = QLinearGradient(0, 0, w, h)
        bg.setColorAt(0, QColor("#061220"))
        bg.setColorAt(0.5, QColor("#0a1e38"))
        bg.setColorAt(1, QColor("#0d2848"))
        painter.fillRect(self.rect(), bg)

        cx, cy = w * 0.48, h * 0.55
        scale = min(w, h) * 0.018 * self._zoom
        rot = self._rot_y + self._rot_x * 0.3

        for i in range(5):
            ring_r = scale * (20 + i * 8)
            alpha = 12 + i * 5
            pen = QPen(QColor(79, 195, 247, alpha))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), ring_r, ring_r * 0.45)

        ground = QPolygonF([
            _iso(-16, 0, -14, cx, cy, scale, rot),
            _iso(16, 0, -14, cx, cy, scale, rot),
            _iso(16, 0, 14, cx, cy, scale, rot),
            _iso(-16, 0, 14, cx, cy, scale, rot),
        ])
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(8, 40, 70, 120))
        painter.drawPolygon(ground)

        self._draw_log_nodes(painter, cx, cy, scale, rot)
        self._draw_flow_lines(painter, cx, cy, scale, rot)
        self._draw_substation(painter, cx, cy, scale, rot, 0, -16)

        painter.setPen(QColor("#4fc3f7"))
        painter.setFont(QFont("Microsoft YaHei UI", 9))
        painter.drawText(12, h - 12, "数据拓扑三维可视化 · 实时数据流")

        glow = QRadialGradient(w * 0.5, h * 0.3, w * 0.4)
        glow.setColorAt(0, QColor(79, 195, 247, 15))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), glow)
        painter.end()

    def _draw_log_nodes(self, painter, cx, cy, scale, rot) -> None:
        nodes = [
            ("日志采集", -10, 0, -8, "#4fc3f7"),
            ("日志解析", 0, 1, -12, "#81c784"),
            ("异常检测", -6, 0.5, 0, "#ffab40"),
            ("故障预测", 6, 0.5, 0, "#ce93d8"),
            ("根因定位", 10, 0, -8, "#ef5350"),
            ("告警中心", 0, 0, 6, "#ffd740"),
            ("知识库", -6, 0, 8, "#8d6e63"),
            ("报表中心", 6, 0, 8, "#4dd0e1"),
        ]
        for name, x, y, z, color in nodes:
            pt = _iso(x, y, z, cx, cy, scale, rot)
            r = 16 + 4 * math.sin(self._phase + hash(name) % 10)
            painter.setBrush(QColor(color))
            painter.setPen(QPen(QColor(color).lighter(120), 1))
            painter.drawEllipse(pt, r, r * 0.7)
            painter.setPen(QColor("#e8edf5"))
            painter.setFont(QFont("Microsoft YaHei UI", 7))
            painter.drawText(QRectF(pt.x() - 40, pt.y() + r + 2, 80, 14), Qt.AlignmentFlag.AlignCenter, name)

    def _draw_flow_lines(self, painter, cx, cy, scale, rot) -> None:
        routes = [
            [(-10, 0.5, -8), (0, 1, -12), (-6, 0.5, 0)],
            [(-10, 0.5, -8), (0, 1, -12), (6, 0.5, 0)],
            [(-6, 0.5, 0), (0, 0, 6)],
            [(6, 0.5, 0), (0, 0, 6)],
            [(0, 0, 6), (-6, 0, 8)],
            [(0, 0, 6), (6, 0, 8)],
        ]
        for ri, route in enumerate(routes):
            intensity = self._flow[ri % len(self._flow)]
            alpha = int(60 + 120 * intensity)
            pen = QPen(QColor(79, 195, 247, alpha), 2)
            painter.setPen(pen)
            for i in range(len(route) - 1):
                p1 = _iso(*route[i], cx, cy, scale, rot)
                p2 = _iso(*route[i + 1], cx, cy, scale, rot)
                painter.drawLine(p1, p2)

            t = (self._phase * 0.3 + ri * 0.2) % 1.0
            idx = min(int(t * (len(route) - 1)), len(route) - 2)
            frac = t * (len(route) - 1) - idx
            p1, p2 = route[idx], route[idx + 1]
            px = p1[0] + (p2[0] - p1[0]) * frac
            py = p1[1] + (p2[1] - p1[1]) * frac
            pz = p1[2] + (p2[2] - p1[2]) * frac
            dot = _iso(px, py, pz, cx, cy, scale, rot)
            radial = QRadialGradient(dot, 8)
            radial.setColorAt(0, QColor(79, 195, 247, 255))
            radial.setColorAt(1, QColor(79, 195, 247, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(radial))
            painter.drawEllipse(dot, 8, 8)

    def _draw_substation(self, painter, cx, cy, scale, rot, x, z) -> None:
        s, h = 4, 5
        base = [
            _iso(x - s, 0, z - s, cx, cy, scale, rot),
            _iso(x + s, 0, z - s, cx, cy, scale, rot),
            _iso(x + s, 0, z + s, cx, cy, scale, rot),
            _iso(x - s, 0, z + s, cx, cy, scale, rot),
        ]
        roof = [
            _iso(x - s, h, z - s, cx, cy, scale, rot),
            _iso(x + s, h, z - s, cx, cy, scale, rot),
            _iso(x + s, h, z + s, cx, cy, scale, rot),
            _iso(x - s, h, z + s, cx, cy, scale, rot),
        ]
        painter.setPen(QPen(QColor("#667788"), 1))
        painter.setBrush(QColor(30, 60, 90, 220))
        painter.drawPolygon(QPolygonF(base))
        painter.setBrush(QColor(40, 70, 100, 200))
        painter.drawPolygon(QPolygonF([base[1], base[2], roof[2], roof[1]]))
        painter.drawPolygon(QPolygonF([base[2], base[3], roof[3], roof[2]]))

        tip = _iso(x, h + 2, z - s, cx, cy, scale, rot)
        mid = _iso(x, h, z - s, cx, cy, scale, rot)
        painter.setPen(QPen(QColor("#4fc3f7"), 2))
        painter.drawLine(mid, tip)

        label = _iso(x, h + 0.5, z, cx, cy, scale, rot)
        painter.setPen(QColor("#4fc3f7"))
        painter.setFont(QFont("Microsoft YaHei UI", 9, QFont.Weight.Bold))
        painter.drawText(QRectF(label.x() - 50, label.y() - 10, 100, 20), Qt.AlignmentFlag.AlignCenter, "LogInsight数据中心")


class VisualizationModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._stats = {"日志采集": 125.4, "解析吞吐": 98.2, "异常事件": 32.0, "系统处理": 215.3}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        top = QHBoxLayout()
        self._scene = TopoSceneCanvas()
        top.addWidget(self._scene, 1)

        ctrl = QGroupBox("场景控制")
        ctrl.setFixedWidth(260)
        cl = QVBoxLayout(ctrl)

        self._rx_slider = QSlider(Qt.Orientation.Horizontal)
        self._rx_slider.setRange(-90, 90)
        self._rx_slider.setValue(20)
        self._ry_slider = QSlider(Qt.Orientation.Horizontal)
        self._ry_slider.setRange(-180, 180)
        self._ry_slider.setValue(-30)
        self._zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self._zoom_slider.setRange(-80, -15)
        self._zoom_slider.setValue(-45)

        cl.addWidget(QLabel("俯仰角"))
        cl.addWidget(self._rx_slider)
        cl.addWidget(QLabel("旋转角"))
        cl.addWidget(self._ry_slider)
        cl.addWidget(QLabel("缩放"))
        cl.addWidget(self._zoom_slider)

        self._rx_slider.valueChanged.connect(lambda v: self._scene.set_rotation(v, self._ry_slider.value()))
        self._ry_slider.valueChanged.connect(lambda v: self._scene.set_rotation(self._rx_slider.value(), v))
        self._zoom_slider.valueChanged.connect(self._scene.set_zoom)

        self._view_combo = QComboBox()
        self._view_combo.addItems(["默认视角", "俯视全景", "采集层特写", "分析引擎层"])
        cl.addWidget(self._view_combo)
        self._view_combo.currentIndexChanged.connect(self._switch_preset)

        top.addWidget(ctrl)
        layout.addLayout(top, 1)

        for buttons in [
            [("重置视角", self._reset_view), ("环绕巡视", self._orbit_tour),
             ("截图保存", self._save_view), ("数据统计", self._show_stats)],
            [("切换布局", self._switch_layout), ("数据叠加", self._overlay_data),
             ("导出拓扑", self._export_topo), ("全屏展示", self._fullscreen_hint)],
        ]:
            r = QHBoxLayout()
            for text, slot in buttons:
                b = QPushButton(text)
                if text == "重置视角":
                    b.setProperty("primary", True)
                b.clicked.connect(slot)
                r.addWidget(b)
            layout.addLayout(r)

        self._info = QLabel("数据拓扑三维可视化 · 智能分析全链路展示")
        self._info.setStyleSheet("color: #8fa8c8; background: transparent;")
        layout.addWidget(self._info)

        self._orbit_timer = QTimer(self)
        self._orbit_timer.timeout.connect(self._orbit_step)
        self._orbit_angle = -30

    def _reset_view(self) -> None:
        self._rx_slider.setValue(20)
        self._ry_slider.setValue(-30)
        self._zoom_slider.setValue(-45)
        self._orbit_timer.stop()

    def _orbit_tour(self) -> None:
        if self._orbit_timer.isActive():
            self._orbit_timer.stop()
            show_info(self, "巡视", "环绕巡视已停止")
        else:
            self._orbit_timer.start(50)
            show_info(self, "巡视", "环绕巡视已启动")

    def _orbit_step(self) -> None:
        self._orbit_angle = (self._orbit_angle + 1) % 360
        self._ry_slider.setValue(self._orbit_angle - 180)

    def _save_view(self) -> None:
        pix = self._scene.grab()
        path = "拓扑可视化截图.png"
        pix.save(path)
        show_info(self, "截图", f"已保存至 {path}")

    def _show_stats(self) -> None:
        lines = ["数据流统计", ""]
        for k, v in self._stats.items():
            unit = "GB/h" if "日志" in k else "MB/s"
            lines.append(f"{k}: {v} {unit}")
        DetailDialog("数据统计", "\n".join(lines), self).exec()

    def _switch_preset(self) -> None:
        presets = {0: (20, -30, -45), 1: (80, 0, -55), 2: (10, -15, -25), 3: (15, 50, -20)}
        idx = self._view_combo.currentIndex()
        rx, ry, zoom = presets.get(idx, (20, -30, -45))
        self._rx_slider.setValue(rx)
        self._ry_slider.setValue(ry)
        self._zoom_slider.setValue(zoom)

    def _switch_layout(self) -> None:
        if self._view_combo.currentIndex() < 3:
            self._view_combo.setCurrentIndex(self._view_combo.currentIndex() + 1)
        else:
            self._view_combo.setCurrentIndex(0)
        show_info(self, "布局", f"已切换至 {self._view_combo.currentText()}")

    def _overlay_data(self) -> None:
        self._info.setText(
            f"日志 {self._stats['日志采集']:.1f} GB/h | "
            f"解析 {self._stats['解析吞吐']:.1f} MB/s | "
            f"异常 {self._stats['异常事件']:.1f} 次/h"
        )

    def _export_topo(self) -> None:
        lines = ["拓扑数据导出", f"时间: 2026-06-23", "",
                 "节点数: 8 (采集/解析/检测/预测/根因/告警/知识库/报表)",
                 "边数: 12 (数据流链路)",
                 "数据格式: GraphML"]
        DetailDialog("拓扑导出", "\n".join(lines), self).exec()

    def _fullscreen_hint(self) -> None:
        show_info(self, "全屏", "请使用窗口最大化按钮进入全屏展示模式")
