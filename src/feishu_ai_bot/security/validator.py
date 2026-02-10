"""安全验证模块

提供访问控制和验证功能
"""

import logging
import time
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feishu_ai_bot.bot.feishu import FeishuBot

logger = logging.getLogger(__name__)


class SecurityValidator:
    """安全验证器
    
    管理访问频率限制、IP白名单、令牌验证等安全功能
    
    Attributes:
        rate_limit_per_minute: 每分钟最大请求数
        enable_ip_whitelist: 是否启用IP白名单
        ip_whitelist: IP白名单列表
        enable_event_verification: 是否启用事件验证
    """
    
    def __init__(
        self,
        rate_limit_per_minute: int = 30,
        enable_ip_whitelist: bool = False,
        ip_whitelist: list = None,
        enable_event_verification: bool = True
    ):
        """初始化安全验证器
        
        Args:
            rate_limit_per_minute: 每分钟最大请求数
            enable_ip_whitelist: 是否启用IP白名单
            ip_whitelist: IP白名单列表
            enable_event_verification: 是否启用事件验证
        """
        self.rate_limit_per_minute = rate_limit_per_minute
        self.enable_ip_whitelist = enable_ip_whitelist
        self.ip_whitelist = ip_whitelist or []
        self.enable_event_verification = enable_event_verification
        
        # 访问频率限制器 {identifier: [timestamp1, timestamp2, ...]}
        self._rate_limiter: dict = defaultdict(list)
    
    def check_rate_limit(self, identifier: str) -> bool:
        """检查访问频率限制
        
        Args:
            identifier: 标识符（如用户ID、IP地址等）
            
        Returns:
            是否允许访问
        """
        current_time = time.time()
        
        # 清理过期的记录（保留最近60秒）
        self._rate_limiter[identifier] = [
            t for t in self._rate_limiter[identifier]
            if current_time - t < 60
        ]
        
        # 检查是否超过限制
        if len(self._rate_limiter[identifier]) >= self.rate_limit_per_minute:
            logger.warning(
                f"访问频率超限: {identifier}, "
                f"请求数: {len(self._rate_limiter[identifier])}"
            )
            return False
        
        # 记录本次访问
        self._rate_limiter[identifier].append(current_time)
        return True
    
    def check_ip_whitelist(self, client_ip: str) -> bool:
        """检查IP是否在白名单中
        
        Args:
            client_ip: 客户端IP地址
            
        Returns:
            是否允许访问
        """
        if not self.enable_ip_whitelist:
            return True
        
        if not self.ip_whitelist:
            return True
        
        if client_ip in self.ip_whitelist:
            return True
        
        logger.warning(f"IP不在白名单中: {client_ip}")
        return False
    
    def validate_event_token(self, bot: "FeishuBot", token: str) -> bool:
        """验证事件令牌
        
        Args:
            bot: FeishuBot实例
            token: 验证令牌
            
        Returns:
            是否验证通过
        """
        if not self.enable_event_verification:
            return True
        
        return bot.verify_verification_token(token)


# 向后兼容的函数接口
_rate_limiter_global = defaultdict(list)


def check_rate_limit(identifier: str, rate_limit_per_minute: int = 30) -> bool:
    """检查访问频率限制（全局函数版本）
    
    Args:
        identifier: 标识符
        rate_limit_per_minute: 每分钟最大请求数
        
    Returns:
        是否允许访问
    """
    current_time = time.time()
    
    # 清理过期的记录
    _rate_limiter_global[identifier] = [
        t for t in _rate_limiter_global[identifier]
        if current_time - t < 60
    ]
    
    # 检查是否超过限制
    if len(_rate_limiter_global[identifier]) >= rate_limit_per_minute:
        logger.warning(
            f"访问频率超限: {identifier}, "
            f"请求数: {len(_rate_limiter_global[identifier])}"
        )
        return False
    
    # 记录本次访问
    _rate_limiter_global[identifier].append(current_time)
    return True


def check_ip_whitelist(client_ip: str, enable: bool = False, whitelist: list = None) -> bool:
    """检查IP白名单（全局函数版本）
    
    Args:
        client_ip: 客户端IP
        enable: 是否启用白名单
        whitelist: 白名单列表
        
    Returns:
        是否允许访问
    """
    if not enable:
        return True
    
    whitelist = whitelist or []
    
    if not whitelist:
        return True
    
    if client_ip in whitelist:
        return True
    
    logger.warning(f"IP不在白名单中: {client_ip}")
    return False
