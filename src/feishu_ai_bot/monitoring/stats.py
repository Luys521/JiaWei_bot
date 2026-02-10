"""监控和统计模块

提供服务状态监控和统计功能
"""

import time
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from feishu_ai_bot.ai.processor import AITaskProcessor
    from feishu_ai_bot.config import AppConfig

logger = logging.getLogger(__name__)


class StatsCollector:
    """统计收集器
    
    收集和提供服务运行统计信息
    
    Attributes:
        start_time: 服务启动时间
        total_requests: 总请求数
        successful_requests: 成功请求数
        failed_requests: 失败请求数
        tasks_processed: 已处理任务数
    """
    
    def __init__(self):
        """初始化统计收集器"""
        self.start_time = datetime.now()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.tasks_processed = 0
    
    def update(self, success: bool = True) -> None:
        """更新统计信息
        
        Args:
            success: 是否成功
        """
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
    
    def increment_tasks(self) -> None:
        """增加已处理任务数"""
        self.tasks_processed += 1
    
    def get_uptime(self) -> float:
        """获取服务运行时间（秒）
        
        Returns:
            运行时间秒数
        """
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_health_status(
        self,
        ai_processor: Optional["AITaskProcessor"] = None
    ) -> Dict[str, Any]:
        """获取健康检查状态
        
        Args:
            ai_processor: AI处理器实例
            
        Returns:
            健康状态字典
        """
        status = {
            "status": "ok",
            "timestamp": time.time(),
            "service": "Feishu AI Bot",
            "version": "1.1.0",
            "uptime": self.get_uptime(),
            "stats": {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "tasks_processed": self.tasks_processed
            }
        }
        
        if ai_processor:
            status["ai_config"] = {
                "provider": getattr(ai_processor, 'ai_provider', 'unknown'),
                "model": getattr(ai_processor, 'model_name', 'unknown'),
                "api_key_configured": bool(getattr(ai_processor, 'api_key', None))
            }
        
        return status
    
    def get_detailed_stats(
        self,
        ai_processor: Optional["AITaskProcessor"] = None,
        config: Optional["AppConfig"] = None
    ) -> Dict[str, Any]:
        """获取详细统计信息
        
        Args:
            ai_processor: AI处理器实例
            config: 应用配置
            
        Returns:
            统计信息字典
        """
        total = self.total_requests
        
        result = {
            "uptime": self.get_uptime(),
            "start_time": self.start_time.isoformat(),
            "requests": {
                "total": total,
                "successful": self.successful_requests,
                "failed": self.failed_requests,
                "success_rate": round(
                    self.successful_requests / total * 100, 2
                ) if total > 0 else 0
            },
            "tasks": {
                "processed": self.tasks_processed
            }
        }
        
        if ai_processor:
            result["ai"] = {
                "provider": getattr(ai_processor, 'ai_provider', 'unknown'),
                "model": getattr(ai_processor, 'model_name', 'unknown'),
                "api_key_configured": bool(getattr(ai_processor, 'api_key', None))
            }
        
        if config:
            result["config"] = {
                "server_port": config.server.port,
                "rate_limit_per_minute": config.security.rate_limit_per_minute,
                "event_verification_enabled": config.security.enable_event_verification,
                "ip_whitelist_enabled": config.security.enable_ip_whitelist
            }
        
        return result


# 全局统计信息（向后兼容）
_service_stats = {
    'start_time': datetime.now(),
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'tasks_processed': 0
}


def update_stats(success: bool = True) -> None:
    """更新服务统计信息（全局函数版本）
    
    Args:
        success: 是否成功
    """
    _service_stats['total_requests'] += 1
    if success:
        _service_stats['successful_requests'] += 1
    else:
        _service_stats['failed_requests'] += 1


def increment_tasks_processed() -> None:
    """增加已处理任务数（全局函数版本）"""
    _service_stats['tasks_processed'] += 1


def get_uptime() -> float:
    """获取服务运行时间（秒）（全局函数版本）
    
    Returns:
        运行时间秒数
    """
    return (datetime.now() - _service_stats['start_time']).total_seconds()


def get_health_status(ai_processor=None) -> Dict[str, Any]:
    """获取健康检查状态（全局函数版本）
    
    Args:
        ai_processor: AI处理器实例
        
    Returns:
        健康状态字典
    """
    collector = StatsCollector()
    # 复制全局统计数据
    collector.start_time = _service_stats['start_time']
    collector.total_requests = _service_stats['total_requests']
    collector.successful_requests = _service_stats['successful_requests']
    collector.failed_requests = _service_stats['failed_requests']
    collector.tasks_processed = _service_stats['tasks_processed']
    
    return collector.get_health_status(ai_processor)


def get_stats(ai_processor=None, server_port: int = 8081) -> Dict[str, Any]:
    """获取详细统计信息（全局函数版本）
    
    Args:
        ai_processor: AI处理器实例
        server_port: 服务器端口
        
    Returns:
        统计信息字典
    """
    from feishu_ai_bot.config import load_config
    
    collector = StatsCollector()
    # 复制全局统计数据
    collector.start_time = _service_stats['start_time']
    collector.total_requests = _service_stats['total_requests']
    collector.successful_requests = _service_stats['successful_requests']
    collector.failed_requests = _service_stats['failed_requests']
    collector.tasks_processed = _service_stats['tasks_processed']
    
    config = load_config()
    return collector.get_detailed_stats(ai_processor, config)
