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

MODULE_REGISTRY = [
    ("collect", "日志采集汇聚", LogCollectorModule),
    ("parser", "日志解析引擎", LogParserModule),
    ("anomaly", "异常检测识别", AnomalyDetectionModule),
    ("search", "日志联机搜索", LogSearchModule),
    ("predict", "故障预测模型", FaultPredictionModule),
    ("cause", "根因定位分析", RootCauseModule),
    ("alarm", "告警管理中心", AlarmCenterModule),
    ("topology", "服务拓扑发现", ServiceTopologyModule),
    ("diagnosis", "智能诊断修复", SmartDiagnosisModule),
    ("dash", "态势感知总览", DashboardModule),
    ("report", "智能报告生成", ReportCenterModule),
    ("kb", "知识图谱构建", KnowledgeBaseModule),
    ("sla", "SLA合规监控", SLAMonitorModule),
    ("train", "模型训练管理", ModelTrainModule),
    ("monitor", "系统监控诊断", SysMonitorModule),
    ("visual", "多维可视化", VisualizationModule),
    ("notify", "告警通知配置", AlertNotifyModule),
    ("custom_dash", "自定义仪表盘", CustomDashboardModule),
    ("config", "配置管理中心", ConfigCenterModule),
    ("audit", "日志审计归档", AuditArchiveModule),
]
