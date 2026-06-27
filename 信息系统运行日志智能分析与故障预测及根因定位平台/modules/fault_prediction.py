import random
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QFormLayout, QDoubleSpinBox, QComboBox,
    QTextEdit, QSplitter, QListWidget, QListWidgetItem, QProgressBar, QSpinBox, QFrame,
)
from PyQt6.QtGui import QColor, QFont
from core.dialogs import show_info, show_success, DetailDialog


class FaultPredictionModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._preds = []
        self._build_ui()
        self._run_prediction()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._run_prediction)
        self._timer.start(5000)

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16,12,16,12)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget(); ll = QVBoxLayout(left)

        # Risk cards
        self._card_row = QHBoxLayout()
        self._risk_cards = []
        for label in ["高风险","中风险","低风险"]:
            card = QFrame()
            card.setStyleSheet("QFrame{background:#121e3a;border:1px solid #2a4070;border-radius:10px;}")
            cl = QVBoxLayout(card); cl.setContentsMargins(12,10,12,10)
            cl.addWidget(QLabel(label, styleSheet="color:#8fa8c8;font-size:10px;"))
            val = QLabel("0"); val.setFont(QFont("Microsoft YaHei",22,QFont.Weight.Bold))
            val.setStyleSheet(f"color:{'#ff5252' if '高' in label else '#ffab40' if '中' in label else '#4fc3f7'};")
            cl.addWidget(val, alignment=Qt.AlignmentFlag.AlignCenter)
            self._risk_cards.append((label,val))
            self._card_row.addWidget(card)
        ll.addLayout(self._card_row)

        # Prediction list
        self._pred_list = QListWidget()
        self._pred_list.setStyleSheet("QListWidget{background:#121e3a;border:1px solid #2a4070;border-radius:8px;}"
            "QListWidget::item{padding:8px 12px;border-bottom:1px solid #1a3060;}"
            "QListWidget::item:hover{background:#1a3060;}")
        ll.addWidget(self._pred_list, 1)

        for buttons in [
            [("执行预测", self._run_prediction), ("趋势分析", self._trend), ("风险评分", self._risk), ("导出", self._export)],
        ]:
            r = QHBoxLayout()
            for t, s in buttons:
                b = QPushButton(t); b.clicked.connect(s)
                if "执行" in t: b.setProperty("primary", True)
                r.addWidget(b)
            ll.addLayout(r)
        splitter.addWidget(left)

        right = QWidget(); rl = QVBoxLayout(right); rl.setContentsMargins(0,0,0,0)
        param_box = QGroupBox("预测参数")
        form = QFormLayout(param_box)
        self._th_spin = QDoubleSpinBox(); self._th_spin.setRange(50,100); self._th_spin.setValue(85); self._th_spin.setSuffix("%")
        form.addRow("故障阈值", self._th_spin)
        self._model_combo = QComboBox(); self._model_combo.addItems(["线性回归","指数平滑","ARIMA","LSTM","集成"])
        form.addRow("模型", self._model_combo)
        rl.addWidget(param_box)

        stat_box = QGroupBox("状态")
        sl = QVBoxLayout(stat_box)
        self._lbl_acc = QLabel("准确率: --"); self._lbl_acc.setStyleSheet("color:#4fc3f7;")
        self._lbl_last = QLabel("最后预测: --"); self._lbl_last.setStyleSheet("color:#8fa8c8;")
        sl.addWidget(self._lbl_acc); sl.addWidget(self._lbl_last)
        rl.addWidget(stat_box)
        self._log = QTextEdit(); self._log.setReadOnly(True); self._log.setMaximumHeight(120)
        rl.addWidget(self._log); rl.addStretch()
        splitter.addWidget(right); layout.addWidget(splitter, 1)

    def _run_prediction(self):
        self._pred_list.clear(); self._preds.clear()
        resources = [
            ("CPU使用率",85), ("内存使用率",85), ("磁盘IO等待",70), ("网络延迟",150),
            ("连接池使用率",90), ("错误率",5), ("JVM堆内存",90), ("GC暂停",500),
            ("线程阻塞数",20), ("缓存命中率",75), ("数据库QPS",6000), ("磁盘使用率",90),
        ]
        high = mid = low = 0
        for name, threshold in resources:
            cur = round(random.uniform(30,95),1)
            trend = random.uniform(-0.5, 1.5)
            risk = "低"
            if trend > 0.8: risk = "高"; high += 1
            elif trend > 0.3: risk = "中"; mid += 1
            else: low += 1
            self._preds.append((name, cur, trend, threshold, risk))
            icon = {"高":"🔴","中":"🟡","低":"🟢"}
            item = QListWidgetItem(f"  {icon[risk]} {name}  当前:{cur}%  趋势:{trend:+.1f}/h  阈值:{threshold}")
            item.setForeground(QColor({"高":"#ff5252","中":"#ffab40","低":"#81c784"}[risk]))
            if risk == "高": item.setBackground(QColor("#2a0000"))
            self._pred_list.addItem(item)
        self._risk_cards[0][1].setText(str(high))
        self._risk_cards[1][1].setText(str(mid))
        self._risk_cards[2][1].setText(str(low))
        self._lbl_acc.setText(f"模型: {self._model_combo.currentText()} 置信度: {random.randint(82,95)}%")
        self._lbl_last.setText(f"最后预测: {datetime.now().strftime('%H:%M:%S')}")
        self._log.append(f"[预测] {len(resources)}项指标分析完成，{high}项高风险")

    def _trend(self):
        lines = ["趋势分析", f"数据点: 30", f"当前值: {random.uniform(50,90):.1f}", f"斜率: {random.uniform(-0.5,1.5):+.2f}/h"]
        DetailDialog("趋势","\n".join(lines),self).exec()
    def _risk(self):
        score = random.uniform(30,95)
        lines = [f"综合风险评分: {score:.0f}/100", f"等级: {'高' if score>70 else '中' if score>40 else '低'}"]
        DetailDialog("风险","\n".join(lines),self).exec()
    def _export(self):
        lines = ["故障预测报告",f"时间:{datetime.now()}",f"模型:{self._model_combo.currentText()}",""]
        for name,cur,trend,th,risk in self._preds:
            lines.append(f"[{risk}] {name}: {cur}% 趋势{trend:+.1f}")
        DetailDialog("报告","\n".join(lines),self).exec()
