# -*- coding: utf-8 -*-
"""
综合截图脚本（修复版）- 注册中文字体后截图
"""
import os, sys, random, time
from datetime import datetime

# 设置为离屏渲染
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '信息系统运行日志智能分析与故障预测及根因定位平台'))

from core.auth import AuthManager
from core.dialogs import show_info, show_success, show_warning, DetailDialog

from modules.log_collector import LogCollectorModule
from modules.log_parser import LogParserModule
from modules.anomaly_detection import AnomalyDetectionModule
from modules.log_search import LogSearchModule
from modules.fault_prediction import FaultPredictionModule
from modules.root_cause import RootCauseModule
from modules.alarm_center import AlarmCenterModule
from modules.service_topology import ServiceTopologyModule
from modules.smart_diagnosis import SmartDiagnosisModule
from modules.dashboard import DashboardModule
from modules.report_center import ReportCenterModule
from modules.knowledge_base import KnowledgeBaseModule
from modules.sla_monitor import SLAMonitorModule
from modules.model_train import ModelTrainModule
from modules.sys_monitor import SysMonitorModule
from modules.visualization import VisualizationModule
from modules.alert_notify import AlertNotifyModule
from modules.custom_dashboard import CustomDashboardModule
from modules.config_center import ConfigCenterModule
from modules.audit_archive import AuditArchiveModule

from ui.login_window import LoginWindow

SCREENSHOT_DIR = 'manual_screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

counter = [0]

def register_chinese_fonts():
    """注册Windows系统中的中文字体"""
    font_dir = 'C:/Windows/Fonts'
    font_files = ['msyh.ttc', 'msyhbd.ttc', 'msyhl.ttc', 'simsun.ttc', 'simhei.ttf', 'simkai.ttf', 'simfang.ttf']
    registered = []
    for fname in font_files:
        path = os.path.join(font_dir, fname)
        if os.path.exists(path):
            fid = QFontDatabase.addApplicationFont(path)
            if fid >= 0:
                families = QFontDatabase.applicationFontFamilies(fid)
                registered.extend(families)
    print(f'已注册字体: {registered}')

def take_shot(widget, name):
    counter[0] += 1
    filename = f"{SCREENSHOT_DIR}/{counter[0]:03d}_{name}.png"
    pixmap = widget.grab()
    pixmap.save(filename)
    QApplication.processEvents()
    print(f"  [{counter[0]:3d}] {filename}")
    return filename

def wait_ms(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()

def close_dialogs():
    for w in QApplication.topLevelWidgets():
        if isinstance(w, QDialog) and w.isVisible():
            w.close()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # 注册中文字体 - 关键！
    register_chinese_fonts()

    # 设置默认字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)

    CONTAINER_W = 1024
    CONTAINER_H = 700

    # 1. 登录页面
    print("\n=== 1. 登录页面 ===")
    login = LoginWindow()
    login.resize(1180, 720)
    login.show()
    QApplication.processEvents()
    wait_ms(800)
    take_shot(login, '01_登录页面')

    # 切换到注册
    for w in login.findChildren(QPushButton):
        if w.text() == '注 册':
            w.click()
            break
    wait_ms(500)
    QApplication.processEvents()
    take_shot(login, '02_注册页面')
    login.close()
    wait_ms(200)

    # 2. 所有模块
    modules_config = [
        (LogCollectorModule, "日志采集汇聚", [
            ("启动采集", lambda m: m._start_all()),
            ("停止采集", lambda m: m._stop_all()),
            ("采集统计", lambda m: m._stats()),
            ("采集配置", lambda m: m._config()),
            ("重置计数器", lambda m: m._reset()),
        ]),
        (LogParserModule, "日志解析引擎", [
            ("执行解析", lambda m: m._parse()),
            ("测试解析", lambda m: m._test()),
            ("解析统计", lambda m: m._stats()),
            ("错误模式", lambda m: m._patterns()),
            ("导出结果", lambda m: m._export()),
        ]),
        (AnomalyDetectionModule, "异常检测识别", [
            ("立即检测", lambda m: m._detect_now()),
            ("检测报告", lambda m: m._report()),
            ("高级配置", lambda m: m._config()),
            ("导出结果", lambda m: m._export()),
        ]),
        (LogSearchModule, "日志联机搜索", [
            ("搜索", lambda m: m._do_search()),
            ("实时Tail", lambda m: m._toggle_tail()),
            ("导出结果", lambda m: m._export()),
            ("语法帮助", lambda m: m._syntax_help()),
        ]),
        (FaultPredictionModule, "故障预测模型", [
            ("执行预测", lambda m: m._run_prediction()),
            ("趋势分析", lambda m: m._trend()),
            ("风险评分", lambda m: m._risk()),
            ("导出报告", lambda m: m._export()),
        ]),
        (RootCauseModule, "根因定位分析", [
            ("根因追溯", lambda m: m._trace()),
            ("关联分析", lambda m: m._correlate()),
            ("故障注入", lambda m: m._inject()),
            ("影响域", lambda m: m._impact()),
            ("导出报告", lambda m: m._export()),
            ("生成因果图", lambda m: m._causal()),
            ("构建拓扑", lambda m: m._build_topo()),
        ]),
        (AlarmCenterModule, "告警管理中心", [
            ("模拟告警", lambda m: m._sim_alarm()),
            ("清理已处理", lambda m: m._clear()),
            ("告警统计", lambda m: m._stats()),
            ("静默模式", lambda m: m._silence()),
            ("规则配置", lambda m: m._rules()),
            ("告警日志", lambda m: m._audit()),
        ]),
        (ServiceTopologyModule, "服务拓扑发现", [
            ("自动发现拓扑", lambda m: m._auto_discover()),
            ("刷新状态", lambda m: m._refresh_status()),
            ("拓扑分析", lambda m: m._analyze()),
            ("导出拓扑", lambda m: m._export()),
        ]),
        (SmartDiagnosisModule, "智能诊断修复", [
            ("智能诊断", lambda m: m._diagnose()),
            ("一键修复", lambda m: m._fix()),
            ("加入知识库", lambda m: m._to_kb()),
            ("批量诊断", lambda m: m._batch_diag()),
            ("导出报告", lambda m: m._export()),
        ]),
        (DashboardModule, "态势感知总览", [
            ("健康检查", lambda m: m._health_check()),
            ("性能快照", lambda m: m._snapshot()),
            ("系统自检", lambda m: m._self_test()),
            ("组件状态", lambda m: m._component_status()),
            ("流量监控", lambda m: m._traffic_monitor()),
            ("综合报告", lambda m: m._gen_report()),
        ]),
        (ReportCenterModule, "智能报告生成", [
            ("生成日报", lambda m: m._gen("日报")),
            ("生成周报", lambda m: m._gen("周报")),
            ("历史报告", lambda m: m._history()),
            ("定时生成", lambda m: m._schedule()),
            ("对比分析", lambda m: m._compare()),
        ]),
        (KnowledgeBaseModule, "知识图谱构建", [
            ("相似度匹配", lambda m: m._match()),
            ("案例学习", lambda m: m._learn()),
            ("新建案例", lambda m: m._add()),
            ("导出知识库", lambda m: m._export()),
            ("重新索引", lambda m: m._reindex()),
        ]),
        (SLAMonitorModule, "SLA合规监控", [
            ("刷新SLO", lambda m: m._refresh()),
            ("新建SLO", lambda m: m._new()),
            ("导出合规报告", lambda m: m._export()),
            ("查看详情", lambda m: m._detail()),
        ]),
        (ModelTrainModule, "模型训练管理", [
            ("开始训练", lambda m: m._start_train()),
            ("模型评估", lambda m: m._eval()),
            ("超参调优", lambda m: m._tune()),
            ("版本对比", lambda m: m._compare()),
            ("训练历史", lambda m: m._history()),
        ]),
        (SysMonitorModule, "系统监控诊断", [
            ("健康诊断", lambda m: m._diagnose()),
            ("资源分析", lambda m: m._resource_analysis()),
            ("性能优化建议", lambda m: m._optimize_suggest()),
            ("进程快照", lambda m: m._process_snapshot()),
            ("网络诊断", lambda m: m._network_diag()),
            ("日志诊断", lambda m: m._log_diag()),
        ]),
        (VisualizationModule, "多维可视化", [
            ("重置视角", lambda m: m._reset_view()),
            ("环绕巡视", lambda m: m._orbit_tour()),
            ("截图保存", lambda m: m._save_view()),
            ("数据统计", lambda m: m._show_stats()),
            ("切换布局", lambda m: m._switch_layout()),
            ("数据叠加", lambda m: m._overlay_data()),
        ]),
        (AlertNotifyModule, "告警通知配置", [
            ("测试通知", lambda m: m._test_notify()),
            ("保存配置", lambda m: m._save_config()),
            ("新建规则", lambda m: m._new_rule()),
            ("编辑规则", lambda m: m._edit_rule()),
        ]),
        (CustomDashboardModule, "自定义仪表盘", [
            ("添加组件", lambda m: m._add_widget()),
            ("保存仪表盘", lambda m: m._save_dash()),
            ("主题切换", lambda m: m._switch_theme()),
            ("导出仪表盘", lambda m: m._export()),
        ]),
        (ConfigCenterModule, "配置管理中心", [
            ("保存修改", lambda m: m._save_config()),
            ("恢复默认", lambda m: m._reset_default()),
            ("导出配置", lambda m: m._export()),
        ]),
        (AuditArchiveModule, "日志审计归档", [
            ("立即归档", lambda m: m._archive_now()),
            ("恢复数据", lambda m: m._restore()),
            ("清理过期", lambda m: m._cleanup()),
            ("归档报告", lambda m: m._report()),
            ("审计日志", lambda m: m._audit()),
            ("归档设置", lambda m: m._settings()),
            ("测试归档", lambda m: m._test()),
        ]),
    ]

    for idx, (module_class, module_name, operations) in enumerate(modules_config, 1):
        print(f"\n=== {idx}. {module_name} ===")

        container = QWidget()
        container.resize(CONTAINER_W, CONTAINER_H)
        container.setStyleSheet("background-color: #0b1426;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        module = module_class(container)
        layout.addWidget(module)
        container.show()
        QApplication.processEvents()
        wait_ms(1000)
        QApplication.processEvents()

        take_shot(container, f'{idx:02d}_{module_name}_主界面')

        for op_idx, (op_name, op_func) in enumerate(operations, 1):
            print(f"  操作 {op_idx}: {op_name}")
            QTimer.singleShot(800, close_dialogs)
            try:
                op_func(module)
            except Exception as e:
                print(f"    ⚠ {e}")
            wait_ms(500)
            QApplication.processEvents()
            take_shot(container, f'{idx:02d}_{module_name}_{op_name}')

        container.close()
        wait_ms(200)
        QApplication.processEvents()

    # 额外截图：模块特定状态
    print("\n=== 额外截图 ===")

    # 日志搜索 - 带结果
    c = QWidget(); c.resize(CONTAINER_W, CONTAINER_H); c.setStyleSheet('background:#0b1426')
    l = QVBoxLayout(c); l.setContentsMargins(0,0,0,0)
    m = LogSearchModule(c); l.addWidget(m); c.show()
    QApplication.processEvents(); wait_ms(300)
    m._search_input.setText('error AND database'); m._do_search()
    wait_ms(500); QApplication.processEvents(); close_dialogs(); wait_ms(200); QApplication.processEvents()
    take_shot(c, '04_日志联机搜索_搜索结果')
    c.close()

    # 故障预测 - 带预测结果
    c = QWidget(); c.resize(CONTAINER_W, CONTAINER_H); c.setStyleSheet('background:#0b1426')
    l = QVBoxLayout(c); l.setContentsMargins(0,0,0,0)
    m = FaultPredictionModule(c); l.addWidget(m); c.show()
    QApplication.processEvents(); wait_ms(1000)
    take_shot(c, '05_故障预测模型_预测状态')
    c.close()

    # 智能诊断 - 完整流程
    c = QWidget(); c.resize(CONTAINER_W, CONTAINER_H); c.setStyleSheet('background:#0b1426')
    l = QVBoxLayout(c); l.setContentsMargins(0,0,0,0)
    m = SmartDiagnosisModule(c); l.addWidget(m); c.show()
    QApplication.processEvents(); wait_ms(300)
    if m._issue_list.count() > 0:
        m._issue_list.setCurrentRow(0); QApplication.processEvents(); wait_ms(200)
        m._diagnose(); wait_ms(500); QApplication.processEvents(); close_dialogs(); wait_ms(200); QApplication.processEvents()
        take_shot(c, '09_智能诊断修复_诊断结果')
        m._fix()
        wait_ms(3000); QApplication.processEvents()
        take_shot(c, '09_智能诊断修复_修复进度')
        wait_ms(3000); QApplication.processEvents(); close_dialogs(); wait_ms(200); QApplication.processEvents()
        take_shot(c, '09_智能诊断修复_修复完成')
    c.close()

    # 配置中心 - 选择配置
    c = QWidget(); c.resize(CONTAINER_W, CONTAINER_H); c.setStyleSheet('background:#0b1426')
    l = QVBoxLayout(c); l.setContentsMargins(0,0,0,0)
    m = ConfigCenterModule(c); l.addWidget(m); c.show()
    QApplication.processEvents(); wait_ms(300)
    root = m._tree.invisibleRootItem()
    if root.childCount() > 0:
        g = root.child(0)
        if g and g.childCount() > 0:
            item = g.child(0); m._tree.setCurrentItem(item); m._show_config(item, 0)
            QApplication.processEvents(); wait_ms(200)
            take_shot(c, '19_配置管理中心_编辑配置')
    c.close()

    # 多维可视化 - 切换视角
    c = QWidget(); c.resize(CONTAINER_W, CONTAINER_H); c.setStyleSheet('background:#0b1426')
    l = QVBoxLayout(c); l.setContentsMargins(0,0,0,0)
    m = VisualizationModule(c); l.addWidget(m); c.show()
    QApplication.processEvents(); wait_ms(500)
    m._view_combo.setCurrentIndex(1); wait_ms(500); QApplication.processEvents()
    take_shot(c, '16_多维可视化_俯视全景')
    m._orbit_tour(); wait_ms(300); QApplication.processEvents()
    take_shot(c, '16_多维可视化_环绕巡视')
    m._orbit_tour(); m._overlay_data(); wait_ms(200); QApplication.processEvents()
    take_shot(c, '16_多维可视化_数据叠加')
    c.close()

    # 自定义仪表盘 - 完整布局
    c = QWidget(); c.resize(CONTAINER_W, CONTAINER_H); c.setStyleSheet('background:#0b1426')
    l = QVBoxLayout(c); l.setContentsMargins(0,0,0,0)
    m = CustomDashboardModule(c); l.addWidget(m); c.show()
    QApplication.processEvents(); wait_ms(500)
    take_shot(c, '18_自定义仪表盘_完整布局')
    c.close()

    print(f"\n✅ 完成！共 {counter[0]} 张截图")
    print(f"保存在: {os.path.abspath(SCREENSHOT_DIR)}/")

if __name__ == '__main__':
    main()
