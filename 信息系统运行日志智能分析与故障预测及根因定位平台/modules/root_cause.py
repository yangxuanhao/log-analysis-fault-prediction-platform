import random
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem,
)
from PyQt6.QtGui import QColor
from core.dialogs import show_info, show_success, show_warning, DetailDialog


class RootCauseModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._incidents = []
        self._init_data()
        self._build_ui()

    def _init_data(self):
        data = [
            ("10:22:15","web_server","502 Bad Gateway","严重"),
            ("10:22:18","api_gateway","上游连接超时","严重"),
            ("10:22:20","auth_service","认证服务无响应","一般"),
            ("10:22:25","order_service","订单查询失败","严重"),
            ("10:22:30","database_primary","主库连接池耗尽","严重"),
            ("10:22:35","payment_service","支付回调超时","一般"),
        ]
        for ts,comp,desc,sev in data:
            self._incidents.append({"时间":ts,"组件":comp,"描述":desc,"严重度":sev})

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(16,12,16,12)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget(); ll = QVBoxLayout(left); ll.setContentsMargins(0,0,0,0)

        # Topology tree
        topo_box = QGroupBox("依赖拓扑")
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["组件"])
        self._tree.setStyleSheet("QTreeWidget{background:#121e3a;border:1px solid #2a4070;border-radius:4px;color:#e8edf5;}"
            "QTreeWidget::item:selected{background:#1a3a6a;}")
        root = QTreeWidgetItem(self._tree,["web_server"])
        gw = QTreeWidgetItem(root,["api_gateway"])
        for s in ["auth_service","user_service","order_service","payment_service"]:
            QTreeWidgetItem(gw,[s])
        db = QTreeWidgetItem(root,["database_primary"])
        QTreeWidgetItem(db,["storage_system"])
        root.setExpanded(True); gw.setExpanded(True)
        topo_box.setLayout(QVBoxLayout()); topo_box.layout().addWidget(self._tree)
        ll.addWidget(topo_box)

        # Result
        result_box = QGroupBox("根因分析结果")
        self._result = QTextEdit()
        self._result.setReadOnly(True); self._result.setPlaceholderText("点击「根因追溯」分析...")
        result_box.setLayout(QVBoxLayout()); result_box.layout().addWidget(self._result)
        ll.addWidget(result_box)

        for buttons in [
            [("根因追溯", self._trace), ("关联分析", self._correlate), ("故障注入", self._inject), ("影响域", self._impact)],
            [("导出报告", self._export), ("生成因果图", self._causal), ("刷新", self._refresh), ("构建拓扑", self._build_topo)],
        ]:
            r = QHBoxLayout()
            for t, s in buttons:
                b = QPushButton(t); b.clicked.connect(s)
                if "根因" in t: b.setProperty("primary", True)
                r.addWidget(b)
            ll.addLayout(r)
        splitter.addWidget(left)

        right = QWidget(); rl = QVBoxLayout(right); rl.setContentsMargins(0,0,0,0)
        inc_box = QGroupBox("当前事件")
        self._inc_list = QListWidget()
        self._inc_list.setStyleSheet("QListWidget{background:#121e3a;border:1px solid #2a4070;border-radius:4px;}"
            "QListWidget::item{padding:6px 10px;border-bottom:1px solid #1a3060;}")
        for inc in self._incidents:
            item = QListWidgetItem(f"  [{inc['严重度']}] {inc['时间']} {inc['组件']}: {inc['描述']}")
            if inc["严重度"]=="严重": item.setForeground(QColor("#ff5252")); item.setBackground(QColor("#2a0000"))
            self._inc_list.addItem(item)
        inc_box.setLayout(QVBoxLayout()); inc_box.layout().addWidget(self._inc_list)
        rl.addWidget(inc_box)
        self._log = QTextEdit(); self._log.setReadOnly(True); self._log.setMaximumHeight(100)
        rl.addWidget(self._log); rl.addStretch()
        splitter.addWidget(right); layout.addWidget(splitter, 1)

    def _trace(self):
        lines = ["根因定位结果:", "", "🔴 [根因] database_primary (影响分数: 1.65)",
                 "🟡 [可能原因] api_gateway (影响分数: 0.85)",
                 "🔵 [关联因素] auth_service (影响分数: 0.45)"]
        self._result.setText("\n".join(lines))
        self._log.append(f"[{datetime.now().strftime('%H:%M:%S')}] 根因追溯完成")
        show_info(self,"根因","定位到3个根因候选，最高置信度92%")
    def _correlate(self):
        lines = ["事件关联:", "  关联度 95%: 主库连接池耗尽 <- 订单查询失败",
                 "  关联度 82%: 上游连接超时 <- 502 Bad Gateway"]
        DetailDialog("关联","\n".join(lines),self).exec()
    def _inject(self):
        target = random.choice(["database_primary","api_gateway","auth_service"])
        self._incidents.insert(0,{"时间":datetime.now().strftime("%H:%M:%S"),"组件":target,
            "描述":f"故障注入: {target}异常","严重度":"严重"})
        self._refresh(); self._log.append(f"[故障注入] {target}")
        show_warning(self,"注入",f"已向{target}注入模拟故障")
    def _impact(self):
        lines = ["影响域分析:", "  database_primary 故障影响:",
                 "    auth_service - 认证服务无响应",
                 "    order_service - 订单查询失败",
                 "    payment_service - 支付回调超时"]
        DetailDialog("影响域","\n".join(lines),self).exec()
    def _export(self):
        lines = ["根因分析报告"]+[f"[{i['严重度']}] {i['时间']} {i['组件']}: {i['描述']}" for i in self._incidents]
        DetailDialog("报告","\n".join(lines),self).exec()
    def _causal(self):
        lines = ["因果图:", "  database_primary 连接池耗尽", "    ├─ auth_service 无响应", "    ├─ order_service 失败", "    └─ api_gateway 超时", "         └─ web_server 502"]
        DetailDialog("因果图","\n".join(lines),self).exec()
    def _refresh(self):
        self._inc_list.clear()
        for inc in self._incidents:
            item = QListWidgetItem(f"  [{inc['严重度']}] {inc['时间']} {inc['组件']}: {inc['描述']}")
            if inc["严重度"]=="严重": item.setForeground(QColor("#ff5252")); item.setBackground(QColor("#2a0000"))
            self._inc_list.addItem(item)
    def _build_topo(self):
        self._log.append("[拓扑] 依赖关系已更新")
