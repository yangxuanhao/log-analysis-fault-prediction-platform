# -*- coding: utf-8 -*-
"""
综合截图脚本 - 为操作手册生成所有模块的操作截图
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

def take_shot(widget, name):
    """截取控件截图"""
    counter[0] += 1
    filename = f"{SCREENSHOT_DIR}/{counter[0]:03d}_{name}.png"
    pixmap = widget.grab()
    pixmap.save(filename)
    # 确保写入磁盘
    QApplication.processEvents()
    print(f"  [{counter[0]:3d}] Saved: {filename}")
    return filename

def take_dialog_shot(name, delay_ms=500):
    """在延迟后截取当前打开的对话框"""
    filename = f"{SCREENSHOT_DIR}/{counter[0]:03d}_{name}.png"
    captured = [False]

    def capture():
        for w in QApplication.topLevelWidgets():
            if isinstance(w, QDialog) and w.isVisible():
                pixmap = w.grab()
                pixmap.save(filename)
                captured[0] = True
                QApplication.processEvents()
                w.close()
                print(f"  [{counter[0]:3d}] Saved: {filename}")
                counter[0] += 1
                break

    QTimer.singleShot(delay_ms, capture)
    return captured, filename

def auto_capture_dialog(name, func, *args, **kwargs):
    """执行一个会弹出对话框的函数并截图"""
    cap, fname = take_dialog_shot(name)
    func(*args, **kwargs)
    # 等待对话框渲染和关闭
    QTest.qWait(600) if hasattr(QTest, 'qWait') else None
    # 简单方式：处理事件
    for _ in range(50):
        QApplication.processEvents()
    return cap[0]

# ---- 简易的事件循环等待 ----
def wait_ms(ms):
    """等待指定毫秒数"""
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()

# ===== 主截图流程 =====
def main():
    app = QApplication(sys.argv)

    # 设置全局样式
    app.setStyle('Fusion')

    # 1. 登录页面截图
    print("\n=== 1. 登录页面 ===")
    login = LoginWindow()
    login.resize(1180, 720)
    login.show()
    QApplication.processEvents()
    QApplication.processEvents()
    wait_ms(500)
    take_shot(login, '01_登录页面')

    # 登录页面-切换到注册
    # 找到AuthForm中的TabSwitch
    for w in login.findChildren(QPushButton):
        if w.text() == '注 册':
            w.click()
            QApplication.processEvents()
            break
    wait_ms(300)
    take_shot(login, '02_注册页面')
    login.close()
    wait_ms(200)

    # 定义一个通用容器尺寸
    CONTAINER_W = 1024
    CONTAINER_H = 700

    # 所有模块的配置 - (模块类, 模块名, 操作列表)
    # 每个操作: (操作名, 操作函数)
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

    # 2. 遍历每个模块截图
    for idx, (module_class, module_name, operations) in enumerate(modules_config, 1):
        print(f"\n=== {idx}. {module_name} ===")

        # 创建容器
        container = QWidget()
        container.resize(CONTAINER_W, CONTAINER_H)
        container.setStyleSheet("background-color: #0b1426;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建模块实例
        module = module_class(container)
        layout.addWidget(module)
        container.show()
        QApplication.processEvents()

        # 等待模块初始化 (给timer一些时间触发)
        wait_ms(800)
        QApplication.processEvents()

        # 截取主界面
        take_shot(container, f'{idx:02d}_{module_name}_主界面')

        # 执行各个操作并截图
        for op_idx, (op_name, op_func) in enumerate(operations, 1):
            print(f"  操作 {op_idx}: {op_name}")

            # 设置对话框自动关闭定时器 (500ms后关闭所有打开的对话框)
            timer_id = QTimer.singleShot(600, lambda: _close_all_dialogs())

            # 执行操作
            try:
                op_func(module)
            except Exception as e:
                print(f"    ⚠ 执行出错: {e}")

            # 等待UI更新和对话框渲染
            wait_ms(400)
            QApplication.processEvents()

            # 截取当前状态 (可能是对话框后的界面)
            take_shot(container, f'{idx:02d}_{module_name}_{op_name}')

        # 清理
        container.close()
        wait_ms(200)
        QApplication.processEvents()

    # 额外截图：模块特定状态
    print("\n=== 额外截图：模块特定状态 ===")

    # 日志搜索 - 先输入关键词再搜索
    container = QWidget()
    container.resize(CONTAINER_W, CONTAINER_H)
    container.setStyleSheet("background-color: #0b1426;")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    m = LogSearchModule(container)
    layout.addWidget(m)
    container.show()
    QApplication.processEvents()
    wait_ms(300)

    # 输入搜索关键词
    m._search_input.setText("error AND database")
    QApplication.processEvents()
    take_shot(container, '04_日志联机搜索_输入关键词')

    # 执行搜索
    m._do_search()
    wait_ms(500)
    QApplication.processEvents()
    take_shot(container, '04_日志联机搜索_搜索结果')
    container.close()
    wait_ms(200)

    # 故障预测 - 执行预测后状态
    container = QWidget()
    container.resize(CONTAINER_W, CONTAINER_H)
    container.setStyleSheet("background-color: #0b1426;")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    m = FaultPredictionModule(container)
    layout.addWidget(m)
    container.show()
    QApplication.processEvents()
    wait_ms(800)
    take_shot(container, '05_故障预测模型_预测状态')
    container.close()
    wait_ms(200)

    # 智能诊断 - 诊断和修复流程
    container = QWidget()
    container.resize(CONTAINER_W, CONTAINER_H)
    container.setStyleSheet("background-color: #0b1426;")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    m = SmartDiagnosisModule(container)
    layout.addWidget(m)
    container.show()
    QApplication.processEvents()
    wait_ms(300)

    # 选中第一个问题并诊断
    if m._issue_list.count() > 0:
        m._issue_list.setCurrentRow(0)
        QApplication.processEvents()
        wait_ms(200)
        m._diagnose()
        wait_ms(300)
        QApplication.processEvents()
        take_shot(container, '09_智能诊断修复_诊断结果')

        # 一键修复
        m._fix()
        wait_ms(100)
        # 等待修复进度条走一部分
        wait_ms(2000)
        QApplication.processEvents()
        take_shot(container, '09_智能诊断修复_修复进度')

        # 等待修复完成
        wait_ms(3000)
        QApplication.processEvents()
        take_shot(container, '09_智能诊断修复_修复完成')
    container.close()
    wait_ms(200)

    # SLA监控 - 带燃烧率图表
    container = QWidget()
    container.resize(CONTAINER_W, CONTAINER_H)
    container.setStyleSheet("background-color: #0b1426;")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    m = SLAMonitorModule(container)
    layout.addWidget(m)
    container.show()
    QApplication.processEvents()
    wait_ms(1000)
    take_shot(container, '13_SLA合规监控_详细状态')
    container.close()
    wait_ms(200)

    # 模型训练 - 训练完成状态
    container = QWidget()
    container.resize(CONTAINER_W, CONTAINER_H)
    container.setStyleSheet("background-color: #0b1426;")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    m = ModelTrainModule(container)
    layout.addWidget(m)
    container.show()
    QApplication.processEvents()
    wait_ms(300)

    # 开始训练并等待完成
    m._start_train()
    wait_ms(300)
    QApplication.processEvents()
    take_shot(container, '14_模型训练管理_训练中')
    # 等待训练完成 (50 epochs * 100ms = 5000ms)
    wait_ms(6000)
    QApplication.processEvents()
    take_shot(container, '14_模型训练管理_训练完成')
    container.close()
    wait_ms(200)

    # 配置中心 - 选择配置项
    container = QWidget()
    container.resize(CONTAINER_W, CONTAINER_H)
    container.setStyleSheet("background-color: #0b1426;")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    m = ConfigCenterModule(container)
    layout.addWidget(m)
    container.show()
    QApplication.processEvents()
    wait_ms(300)

    # 选择一个配置项
    root = m._tree.invisibleRootItem()
    if root.childCount() > 0:
        group = root.child(0)
        if group and group.childCount() > 0:
            item = group.child(0)
            m._tree.setCurrentItem(item)
            m._show_config(item, 0)
            QApplication.processEvents()
            wait_ms(200)
            take_shot(container, '19_配置管理中心_编辑配置')
    container.close()
    wait_ms(200)

    # 多维可视化 - 特殊场景
    container = QWidget()
    container.resize(CONTAINER_W, CONTAINER_H)
    container.setStyleSheet("background-color: #0b1426;")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    m = VisualizationModule(container)
    layout.addWidget(m)
    container.show()
    QApplication.processEvents()
    wait_ms(500)

    # 切换到俯视全景
    m._view_combo.setCurrentIndex(1)
    wait_ms(500)
    QApplication.processEvents()
    take_shot(container, '16_多维可视化_俯视全景')

    # 启动环绕模式
    m._orbit_tour()
    wait_ms(500)
    QApplication.processEvents()
    take_shot(container, '16_多维可视化_环绕巡视')

    # 停止环绕
    m._orbit_tour()
    wait_ms(300)

    # 数据叠加
    m._overlay_data()
    wait_ms(200)
    QApplication.processEvents()
    take_shot(container, '16_多维可视化_数据叠加')
    container.close()
    wait_ms(200)

    # 自定义仪表盘 - 添加组件后
    container = QWidget()
    container.resize(CONTAINER_W, CONTAINER_H)
    container.setStyleSheet("background-color: #0b1426;")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    m = CustomDashboardModule(container)
    layout.addWidget(m)
    container.show()
    QApplication.processEvents()
    wait_ms(500)
    take_shot(container, '18_自定义仪表盘_完整布局')
    container.close()
    wait_ms(200)

    print(f"\n\n✅ 截图完成！总共生成 {counter[0]} 张截图")
    print(f"截图保存在: {os.path.abspath(SCREENSHOT_DIR)}/")


def _close_all_dialogs():
    """关闭所有打开的对话框"""
    for w in QApplication.topLevelWidgets():
        if isinstance(w, QDialog) and w.isVisible():
            w.close()


if __name__ == '__main__':
    main()
