import random, math
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QFormLayout, QComboBox, QTextEdit, QSplitter,
    QListWidget, QListWidgetItem, QProgressBar, QSpinBox, QDoubleSpinBox,
)
from PyQt6.QtGui import QColor
from core.dialogs import show_info, show_success, show_warning, DetailDialog


MODELS = {
    "AnomalyDetect-v1": {"类型":"异常检测","算法":"Isolation Forest","准确率":"85%","状态":"已部署"},
    "AnomalyDetect-v2": {"类型":"异常检测","算法":"XGBoost","准确率":"91%","状态":"已部署"},
    "FaultPredict-LSTM": {"类型":"故障预测","算法":"LSTM","准确率":"88%","状态":"训练中"},
    "FaultPredict-ARIMA": {"类型":"故障预测","算法":"ARIMA","准确率":"82%","状态":"已部署"},
    "RootCause-BN": {"类型":"根因定位","算法":"贝叶斯网络","准确率":"86%","状态":"已部署"},
}


class ModelTrainModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._training = False
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16,12,16,12)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget(); ll = QVBoxLayout(left); ll.setContentsMargins(0,0,0,0)

        self._model_list = QListWidget()
        self._model_list.setStyleSheet("QListWidget{background:#121e3a;border:1px solid #2a4070;border-radius:8px;}"
            "QListWidget::item{padding:8px 14px;border-bottom:1px solid #1a3060;}"
            "QListWidget::item:hover{background:#1a3060;}")
        ll.addWidget(self._model_list, 1)

        for buttons in [
            [("开始训练", self._start_train), ("停止", self._stop_train), ("模型评估", self._eval), ("部署", self._deploy)],
            [("超参调优", self._tune), ("版本对比", self._compare), ("导出", self._export), ("训练历史", self._history)],
        ]:
            r = QHBoxLayout()
            for t, s in buttons:
                b = QPushButton(t); b.clicked.connect(s)
                if "开始" in t: b.setProperty("primary", True)
                r.addWidget(b)
            ll.addLayout(r)
        splitter.addWidget(left)

        right = QWidget(); rl = QVBoxLayout(right); rl.setContentsMargins(0,0,0,0)
        config_box = QGroupBox("训练配置")
        form = QFormLayout(config_box)
        self._name_cb = QComboBox(); self._name_cb.addItems(["AnomalyDetect-v3","FaultPredict-Transformer","RootCause-GNN"])
        form.addRow("模型", self._name_cb)
        self._algo_cb = QComboBox(); self._algo_cb.addItems(["XGBoost","LightGBM","LSTM","Transformer","GNN"])
        form.addRow("算法", self._algo_cb)
        self._epoch_spin = QSpinBox(); self._epoch_spin.setRange(10,500); self._epoch_spin.setValue(50)
        form.addRow("轮次", self._epoch_spin)
        rl.addWidget(config_box)

        progress_box = QGroupBox("训练进度")
        pl = QVBoxLayout(progress_box)
        self._prog_bar = QProgressBar(); self._prog_bar.setRange(0,100); self._prog_bar.setValue(0)
        pl.addWidget(self._prog_bar)
        self._prog_label = QLabel("就绪"); self._prog_label.setStyleSheet("color:#4fc3f7;")
        pl.addWidget(self._prog_label)
        rl.addWidget(progress_box)

        metric_box = QGroupBox("评估指标")
        ml = QVBoxLayout(metric_box)
        self._lbl_prec = QLabel("精确率: --"); self._lbl_rec = QLabel("召回率: --"); self._lbl_f1 = QLabel("F1: --")
        for lb in [self._lbl_prec,self._lbl_rec,self._lbl_f1]:
            lb.setStyleSheet("color:#4fc3f7;"); ml.addWidget(lb)
        rl.addWidget(metric_box)

        self._log = QTextEdit(); self._log.setReadOnly(True); self._log.setMaximumHeight(100)
        rl.addWidget(self._log); rl.addStretch()
        splitter.addWidget(right); layout.addWidget(splitter, 1)
        self._epochs = 0

    def _refresh_list(self):
        self._model_list.clear()
        for name, info in MODELS.items():
            icon = {"已部署":"✅","训练中":"🔄","训练完成":"📊"}
            item = QListWidgetItem(f"  {icon.get(info['状态'],'○')} {name} [{info['类型']}] {info['算法']} {info['准确率']}")
            if info["状态"]=="训练中": item.setForeground(QColor("#ffab40"))
            elif info["状态"]=="已部署": item.setForeground(QColor("#4fc3f7"))
            self._model_list.addItem(item)

    def _start_train(self):
        if self._training: show_warning(self,"提示","已有训练任务"); return
        self._training = True; self._epochs = self._epoch_spin.value()
        self._prog_bar.setValue(0); self._log.append(f"[训练] 开始 {self._name_cb.currentText()}")
        self._train_timer = QTimer(self); self._train_timer._step = 0
        self._train_timer.timeout.connect(self._train_step)
        self._train_timer.start(100)

    def _train_step(self):
        self._train_timer._step += 1
        prog = min(100, int(self._train_timer._step / self._epochs * 100))
        self._prog_bar.setValue(prog)
        self._prog_label.setText(f"训练中... {self._train_timer._step}/{self._epochs}")
        if self._train_timer._step >= self._epochs:
            self._train_timer.stop(); self._training = False
            self._prog_label.setText("✅ 完成")
            self._lbl_prec.setText(f"精确率: {random.uniform(85,96):.1f}%")
            self._lbl_rec.setText(f"召回率: {random.uniform(82,94):.1f}%")
            self._lbl_f1.setText(f"F1: {random.uniform(0.83,0.95):.2f}")
            self._log.append(f"[完成] {self._name_cb.currentText()} 训练完成")
            MODELS[self._name_cb.currentText()] = {"类型":"自定义","算法":self._algo_cb.currentText(),
                "准确率":f"{random.randint(85,95)}%","状态":"训练完成"}
            self._refresh_list()
            show_success(self,"完成","模型训练完成")

    def _stop_train(self):
        if hasattr(self,'_train_timer') and self._train_timer.isActive():
            self._train_timer.stop(); self._training=False; self._prog_label.setText("已停止")
            self._log.append("[训练已停止]")

    def _eval(self):
        prec=random.uniform(85,96); rec=random.uniform(82,94); f1=2*prec*rec/(prec+rec)/100
        lines=[f"精确率: {prec:.1f}%",f"召回率: {rec:.1f}%",f"F1: {f1:.4f}"]
        DetailDialog("评估","\n".join(lines),self).exec()

    def _deploy(self):
        show_success(self,"部署","模型已发布到生产环境")
    def _tune(self):
        lines=["超参调优结果:","Learning Rate: 0.001->0.0008","Batch Size: 32->64","F1提升: +0.023"]
        DetailDialog("调优","\n".join(lines),self).exec()
    def _compare(self):
        lines=["版本对比:","AnomalyDetect-v1: 85%","AnomalyDetect-v2: 91% ↑6%"]
        DetailDialog("对比","\n".join(lines),self).exec()
    def _export(self):
        show_success(self,"导出","模型文件已导出")
    def _history(self):
        lines=["训练历史:"]+[f"  Epoch {i}: acc={0.5+0.4*i/50:.4f}" for i in range(1,21)]
        DetailDialog("历史","\n".join(lines),self).exec()
