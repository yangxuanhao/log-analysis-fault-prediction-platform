import random
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QTextEdit, QSplitter, QProgressBar, QFrame,
    QListWidget, QListWidgetItem,
)
from PyQt6.QtGui import QColor, QPainter, QPen, QFont
from core.dialogs import show_info, show_success, DetailDialog


class SLABurnChart(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setMinimumHeight(90)
        self._data = [random.uniform(0.85,1.0) for _ in range(30)]
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h = self.width(),self.height()
        painter.fillRect(self.rect(), QColor("#121e3a"))
        m=25; pw,ph=w-m*2,h-30
        painter.setPen(QPen(QColor("#2a4070"),1))
        for i in range(4): painter.drawLine(m,int(m+ph*i/3),w-m,int(m+ph*i/3))
        painter.setPen(QPen(QColor("#ff5252"),1,Qt.PenStyle.DashLine))
        sy=m+ph*(1-0.95); painter.drawLine(m,int(sy),w-m,int(sy))
        painter.setPen(QColor("#ff5252")); painter.setFont(QFont("Microsoft YaHei",7))
        painter.drawText(w-m+2,int(sy)-2,"SLO 95%")
        painter.setPen(QPen(QColor("#4fc3f7"),2))
        for i in range(1,len(self._data)):
            x1=m+pw*(i-1)/(len(self._data)-1); y1=m+ph*(1-self._data[i-1])
            x2=m+pw*i/(len(self._data)-1); y2=m+ph*(1-self._data[i])
            c="#ff5252" if self._data[i]<0.95 else "#4fc3f7"
            painter.setPen(QPen(QColor(c),2))
            painter.drawLine(int(x1),int(y1),int(x2),int(y2))
        painter.end()


class SLAMonitorModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._slos = [
            {"name":"API可用性","slo":99.9,"cur":99.87,"budget":72.3,"status":"警告"},
            {"name":"日志处理延迟","slo":99.5,"cur":99.62,"budget":88.5,"status":"正常"},
            {"name":"异常检测召回率","slo":95.0,"cur":96.8,"budget":91.2,"status":"正常"},
            {"name":"系统可用率","slo":99.99,"cur":99.97,"budget":45.8,"status":"危险"},
            {"name":"故障预测准确率","slo":90.0,"cur":92.5,"budget":95.0,"status":"正常"},
            {"name":"告警处理时效","slo":98.0,"cur":97.2,"budget":62.1,"status":"警告"},
        ]
        self._build_ui()
        self._timer = QTimer(self); self._timer.timeout.connect(self._tick); self._timer.start(5000)

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16,12,16,12)
        self._chart = SLABurnChart(); layout.addWidget(self._chart)

        # SLO cards grid
        grid = QHBoxLayout()
        for slo in self._slos[:3]:
            card = self._card(slo); grid.addWidget(card)
        layout.addLayout(grid)
        grid2 = QHBoxLayout()
        for slo in self._slos[3:]:
            card = self._card(slo); grid2.addWidget(card)
        layout.addLayout(grid2)

        # List
        self._slo_list = QListWidget()
        self._slo_list.setStyleSheet("QListWidget{background:#121e3a;border:1px solid #2a4070;border-radius:8px;}"
            "QListWidget::item{padding:8px 12px;border-bottom:1px solid #1a3060;}")
        self._refresh_list()
        layout.addWidget(self._slo_list, 1)

        for buttons in [
            [("刷新SLO", self._refresh), ("新建SLO", self._new), ("导出合规报告", self._export), ("查看详情", self._detail)]
        ]:
            r = QHBoxLayout()
            for t, s in buttons:
                b = QPushButton(t); b.clicked.connect(s)
                if "刷新" in t: b.setProperty("primary", True)
                r.addWidget(b)
            layout.addLayout(r)

    def _card(self, slo):
        card = QFrame(); card.setStyleSheet("QFrame{background:#121e3a;border:1px solid #2a4070;border-radius:10px;}")
        cl = QVBoxLayout(card); cl.setContentsMargins(14,12,14,12)
        name = QLabel(slo["name"]); name.setStyleSheet("color:#8fa8c8;font-size:11px;")
        colors = {"正常":"#4fc3f7","警告":"#ffab40","危险":"#ff5252"}
        val = QLabel(f"{slo['cur']}%"); val.setStyleSheet(f"color:{colors.get(slo['status'],'#8fa8c8')};font-size:20px;font-weight:bold;")
        bar = QProgressBar(); bar.setRange(0,100); bar.setValue(int(slo['cur'])); bar.setTextVisible(False); bar.setFixedHeight(6)
        meta = QLabel(f"SLO:{slo['slo']}%  预算:{slo['budget']}%")
        meta.setStyleSheet(f"color:{colors.get(slo['status'],'#8fa8c8')};font-size:9px;")
        cl.addWidget(name); cl.addWidget(val); cl.addWidget(bar); cl.addWidget(meta)
        return card

    def _refresh_list(self):
        self._slo_list.clear()
        for slo in self._slos:
            icon = {"正常":"🟢","警告":"🟡","危险":"🔴"}
            item = QListWidgetItem(f"  {icon.get(slo['status'],'○')} {slo['name']}: {slo['cur']}% (SLO:{slo['slo']}%) 预算:{slo['budget']}%")
            item.setForeground(QColor({"正常":"#4fc3f7","警告":"#ffab40","危险":"#ff5252"}[slo['status']]))
            self._slo_list.addItem(item)

    def _refresh(self):
        for slo in self._slos:
            slo["cur"] = round(min(100,max(85,slo["cur"]+random.uniform(-0.3,0.2))),2)
            slo["budget"] = max(0,slo["budget"]-random.uniform(0,2))
            slo["status"] = "危险" if slo["budget"]<30 else ("警告" if slo["budget"]<70 else "正常")
        self._refresh_list()
        show_success(self,"刷新","SLO已更新")
    def _new(self): show_info(self,"新建","指标名称:\nSLO目标(%):\n时间窗口: 30天")
    def _export(self):
        lines = ["SLA合规报告"]+[f"{s['name']}: {s['cur']}% (SLO:{s['slo']}%) [{s['status']}]" for s in self._slos]
        DetailDialog("报告","\n".join(lines),self).exec()
    def _detail(self):
        cur = self._slo_list.currentRow()
        if cur<0: return
        s = self._slos[cur]
        show_info(self,s["name"],f"当前值: {s['cur']}%\nSLO目标: {s['slo']}%\n错误预算: {s['budget']}%\n状态: {s['status']}")
    def _tick(self):
        s = random.choice(self._slos)
        s["cur"] = round(min(100,max(85,s["cur"]+random.uniform(-0.1,0.1))),2)
        s["budget"] = max(0,s["budget"]-random.uniform(0,0.5))
        s["status"] = "危险" if s["budget"]<30 else ("警告" if s["budget"]<70 else "正常")
