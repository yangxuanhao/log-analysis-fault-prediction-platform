# -*- coding: utf-8 -*-
"""补充截图"""
import os, sys
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '信息系统运行日志智能分析与故障预测及根因定位平台'))

from modules.log_search import LogSearchModule
from modules.fault_prediction import FaultPredictionModule
from modules.smart_diagnosis import SmartDiagnosisModule
from modules.sla_monitor import SLAMonitorModule
from modules.model_train import ModelTrainModule
from modules.config_center import ConfigCenterModule
from modules.visualization import VisualizationModule
from modules.custom_dashboard import CustomDashboardModule

app = QApplication(sys.argv)
app.setStyle('Fusion')

OUT = 'manual_screenshots'
counter = [122]

def shot(w, name):
    counter[0] += 1
    f = f'{OUT}/{counter[0]:03d}_{name}.png'
    w.grab().save(f)
    print(f'[{counter[0]}] {f}')

def wait(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()

def close_dialogs():
    for w in QApplication.topLevelWidgets():
        if isinstance(w, QDialog) and w.isVisible():
            w.close()

# 1. 日志搜索
print('=== 日志搜索 ===')
c = QWidget()
c.resize(1024, 700)
c.setStyleSheet('background:#0b1426')
l = QVBoxLayout(c)
m = LogSearchModule(c)
l.addWidget(m)
c.show()
QApplication.processEvents()
wait(300)
m._search_input.setText('error AND database')
m._do_search()
wait(500)
QApplication.processEvents()
close_dialogs()
wait(200)
QApplication.processEvents()
shot(c, '04_日志联机搜索_搜索结果')
c.close()

# 2. 故障预测
print('=== 故障预测 ===')
c = QWidget()
c.resize(1024, 700)
c.setStyleSheet('background:#0b1426')
l = QVBoxLayout(c)
m = FaultPredictionModule(c)
l.addWidget(m)
c.show()
QApplication.processEvents()
wait(1000)
shot(c, '05_故障预测模型_预测状态')
c.close()

# 3. 智能诊断
print('=== 智能诊断 ===')
c = QWidget()
c.resize(1024, 700)
c.setStyleSheet('background:#0b1426')
l = QVBoxLayout(c)
m = SmartDiagnosisModule(c)
l.addWidget(m)
c.show()
QApplication.processEvents()
wait(300)
if m._issue_list.count() > 0:
    m._issue_list.setCurrentRow(0)
    QApplication.processEvents()
    wait(200)
    m._diagnose()
    wait(500)
    QApplication.processEvents()
    close_dialogs()
    wait(200)
    QApplication.processEvents()
    shot(c, '09_智能诊断修复_诊断结果')
    m._fix()
    wait(3000)
    QApplication.processEvents()
    shot(c, '09_智能诊断修复_修复进度')
    wait(3000)
    QApplication.processEvents()
    close_dialogs()
    wait(200)
    QApplication.processEvents()
    shot(c, '09_智能诊断修复_修复完成')
c.close()

# 4. SLA
print('=== SLA ===')
c = QWidget()
c.resize(1024, 700)
c.setStyleSheet('background:#0b1426')
l = QVBoxLayout(c)
m = SLAMonitorModule(c)
l.addWidget(m)
c.show()
QApplication.processEvents()
wait(1000)
shot(c, '13_SLA合规监控_详细状态')
c.close()

# 5. 模型训练
print('=== 模型训练 ===')
c = QWidget()
c.resize(1024, 700)
c.setStyleSheet('background:#0b1426')
l = QVBoxLayout(c)
m = ModelTrainModule(c)
l.addWidget(m)
c.show()
QApplication.processEvents()
wait(300)
m._start_train()
wait(300)
QApplication.processEvents()
shot(c, '14_模型训练管理_训练中')
wait(6000)
QApplication.processEvents()
shot(c, '14_模型训练管理_训练完成')
c.close()

# 6. 配置中心
print('=== 配置中心 ===')
c = QWidget()
c.resize(1024, 700)
c.setStyleSheet('background:#0b1426')
l = QVBoxLayout(c)
m = ConfigCenterModule(c)
l.addWidget(m)
c.show()
QApplication.processEvents()
wait(300)
root = m._tree.invisibleRootItem()
if root.childCount() > 0:
    g = root.child(0)
    if g and g.childCount() > 0:
        item = g.child(0)
        m._tree.setCurrentItem(item)
        m._show_config(item, 0)
        QApplication.processEvents()
        wait(200)
        shot(c, '19_配置管理中心_编辑配置')
c.close()

# 7. 多维可视化
print('=== 多维可视化 ===')
c = QWidget()
c.resize(1024, 700)
c.setStyleSheet('background:#0b1426')
l = QVBoxLayout(c)
m = VisualizationModule(c)
l.addWidget(m)
c.show()
QApplication.processEvents()
wait(500)
m._view_combo.setCurrentIndex(1)
wait(500)
QApplication.processEvents()
shot(c, '16_多维可视化_俯视全景')
m._orbit_tour()
wait(300)
QApplication.processEvents()
shot(c, '16_多维可视化_环绕巡视')
m._orbit_tour()
m._overlay_data()
wait(200)
QApplication.processEvents()
shot(c, '16_多维可视化_数据叠加')
c.close()

# 8. 自定义仪表盘
print('=== 自定义仪表盘 ===')
c = QWidget()
c.resize(1024, 700)
c.setStyleSheet('background:#0b1426')
l = QVBoxLayout(c)
m = CustomDashboardModule(c)
l.addWidget(m)
c.show()
QApplication.processEvents()
wait(500)
shot(c, '18_自定义仪表盘_完整布局')
c.close()

print(f'\n完成! 共 {counter[0]} 张截图')
