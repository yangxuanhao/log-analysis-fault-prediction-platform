# 信息系统运行日志智能分析与故障预测及根因定位平台

基于 Python3 + PyQt6 的企业级信息系统运行日志智能分析平台，集日志收集、异常检测、故障预测、根因定位、智能诊断和可视化于一体。

## 功能模块

| 模块 | 功能说明 |
|------|---------|
| **日志收集** (log_collector) | 多源日志采集与统一接入 |
| **日志解析** (log_parser) | 日志格式解析与结构化处理 |
| **日志搜索** (log_search) | 全文检索与多维过滤 |
| **异常检测** (anomaly_detection) | 基于规则的实时异常发现 |
| **故障预测** (fault_prediction) | 趋势分析与故障预判 |
| **根因定位** (root_cause) | 故障根因自动分析 |
| **智能诊断** (smart_diagnosis) | AI 辅助诊断建议 |
| **告警通知** (alert_notify) | 多通道告警推送 |
| **告警中心** (alarm_center) | 告警聚合与管理 |
| **系统监控** (sys_monitor) | 系统运行状态实时监控 |
| **服务拓扑** (service_topology) | 服务依赖关系可视化 |
| **SLA 监控** (sla_monitor) | 服务等级协议达标监控 |
| **知识库** (knowledge_base) | 故障案例与解决方案库 |
| **模型训练** (model_train) | 预测模型训练与优化 |
| **可视化** (visualization) | 数据图表与趋势展示 |
| **仪表盘** (dashboard) | 全局运行状态总览 |
| **自定义仪表盘** (custom_dashboard) | 个性化看板配置 |
| **配置中心** (config_center) | 系统配置集中管理 |
| **审计归档** (audit_archive) | 操作审计与日志归档 |
| **报告中心** (report_center) | 自动生成分析报告 |

## 技术栈

- **编程语言**: Python 3
- **GUI 框架**: PyQt6 (>= 6.6.0)
- **架构**: 模块化设计，core + modules + ui 三层架构

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python main.py
```

## 系统架构

```
├── core/          # 核心组件（认证、常量、样式等）
├── modules/       # 业务模块（20+ 功能模块）
├── ui/            # 界面层（登录、主窗口等）
└── main.py        # 程序入口
```
