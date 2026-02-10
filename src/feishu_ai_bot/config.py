"""配置管理模块

使用 dataclass 管理应用配置，替代原来的全局变量方式。
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()


@dataclass
class FeishuConfig:
    """飞书配置"""
    app_id: str = ""
    app_secret: str = ""
    encrypt_key: str = ""
    verification_token: str = ""
    bot_open_id: str = ""
    target_chat_id: str = ""


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8081
    log_level: str = "INFO"
    log_file: str = "/var/log/feishu-ai-bot/bot.log"
    debug: bool = False


@dataclass
class AIConfig:
    """AI配置"""
    provider: str = "deepseek"
    api_key: str = ""
    api_base: str = ""
    model_name: str = ""
    timeout: int = 30
    max_retries: int = 3


@dataclass
class OpenClawConfig:
    """OpenClaw配置"""
    enabled: bool = True
    gateway_url: str = "http://localhost:18789"
    token: str = ""
    agent_id: str = "main"
    timeout: int = 90


@dataclass
class SecurityConfig:
    """安全配置"""
    enable_event_verification: bool = True
    rate_limit_per_minute: int = 30
    enable_ip_whitelist: bool = False
    ip_whitelist: List[str] = field(default_factory=list)


@dataclass
class MessageTemplates:
    """消息模板配置"""
    welcome: str = """👋 你好！我是AI助手小跃，我可以帮你：

📊 数据分析与处理
💻 编写和执行代码
🔍 搜索信息和资料
📁 文件操作和管理
📝 文档生成和编辑
🤖 自动化任务执行

只需@我并描述你的需求，我会立即为你处理！
"""
    task_received: str = "✅ 收到任务！正在为你处理，请稍候..."
    task_processing: str = "⏳ 任务处理中，预计需要 {time} 秒..."
    task_completed: str = "✨ 任务已完成！"
    task_failed: str = "❌ 任务执行失败：{error}"


@dataclass
class AppConfig:
    """应用主配置"""
    name: str = "feishu-ai-bot"
    version: str = "1.1.0"
    env: str = "development"
    workspace_dir: str = "/root/feishu_ai_bot"
    
    feishu: FeishuConfig = field(default_factory=FeishuConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    openclaw: OpenClawConfig = field(default_factory=OpenClawConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    messages: MessageTemplates = field(default_factory=MessageTemplates)


def load_config() -> AppConfig:
    """从环境变量加载配置
    
    Returns:
        应用配置对象
    """
    config = AppConfig()
    
    # 应用信息
    config.name = os.getenv("APP_NAME", "feishu-ai-bot")
    config.version = os.getenv("APP_VERSION", "1.1.0")
    config.env = os.getenv("APP_ENV", "development")
    config.workspace_dir = os.getenv("WORKSPACE_DIR", "/root/feishu_ai_bot")
    
    # 飞书配置
    config.feishu = FeishuConfig(
        app_id=os.getenv("FEISHU_APP_ID", ""),
        app_secret=os.getenv("FEISHU_APP_SECRET", ""),
        encrypt_key=os.getenv("FEISHU_ENCRYPT_KEY", ""),
        verification_token=os.getenv("FEISHU_VERIFICATION_TOKEN", ""),
        bot_open_id=os.getenv("FEISHU_BOT_OPEN_ID", ""),
        target_chat_id=os.getenv("TARGET_CHAT_ID", ""),
    )
    
    # 服务器配置
    config.server = ServerConfig(
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", "8081")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE", "/var/log/feishu-ai-bot/bot.log"),
        debug=os.getenv("APP_ENV", "development") == "development",
    )
    
    # AI配置
    config.ai = AIConfig(
        provider=os.getenv("AI_PROVIDER", "deepseek"),
        api_key=os.getenv("AI_API_KEY", ""),
        api_base=os.getenv("AI_API_BASE", ""),
        model_name=os.getenv("AI_MODEL_NAME", ""),
        timeout=int(os.getenv("AI_TIMEOUT", "30")),
        max_retries=int(os.getenv("AI_MAX_RETRIES", "3")),
    )
    
    # 设置默认API地址和模型
    if config.ai.provider == "deepseek" and not config.ai.api_base:
        config.ai.api_base = "https://api.deepseek.com/v1"
        if not config.ai.model_name:
            config.ai.model_name = "deepseek-chat"
    elif config.ai.provider == "minimax" and not config.ai.api_base:
        config.ai.api_base = "https://api.minimax.chat/v1"
        if not config.ai.model_name:
            config.ai.model_name = "abab5.5-chat"
    elif config.ai.provider == "openai" and not config.ai.api_base:
        config.ai.api_base = "https://api.openai.com/v1"
        if not config.ai.model_name:
            config.ai.model_name = "gpt-3.5-turbo"
    
    # OpenClaw配置
    config.openclaw = OpenClawConfig(
        enabled=os.getenv("OPENCLAW_ENABLED", "true").lower() == "true",
        gateway_url=os.getenv("OPENCLAW_GATEWAY_URL", "http://localhost:18789"),
        token=os.getenv("OPENCLAW_TOKEN", ""),
        agent_id=os.getenv("OPENCLAW_AGENT_ID", "main"),
        timeout=int(os.getenv("OPENCLAW_TIMEOUT", "90")),
    )
    
    # 安全配置
    ip_whitelist_str = os.getenv("IP_WHITELIST", "")
    config.security = SecurityConfig(
        enable_event_verification=os.getenv("ENABLE_EVENT_VERIFICATION", "true").lower() == "true",
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "30")),
        enable_ip_whitelist=os.getenv("ENABLE_IP_WHITELIST", "false").lower() == "true",
        ip_whitelist=ip_whitelist_str.split(",") if ip_whitelist_str else [],
    )
    
    return config


def validate_config(config: AppConfig) -> Tuple[bool, List[str]]:
    """验证配置是否完整
    
    Args:
        config: 应用配置对象
        
    Returns:
        (是否有效, 错误列表)
    """
    errors = []
    
    # 验证飞书配置
    if not config.feishu.app_id:
        errors.append("FEISHU_APP_ID 未配置（必填）")
    
    if not config.feishu.app_secret:
        errors.append("FEISHU_APP_SECRET 未配置（必填）")
    
    if not config.feishu.target_chat_id:
        errors.append("TARGET_CHAT_ID 未配置（必填）")
    
    if not config.feishu.bot_open_id:
        errors.append("FEISHU_BOT_OPEN_ID 未配置（必填）")
    
    # 验证AI配置
    if not config.ai.api_key:
        errors.append("AI_API_KEY 未配置（必填），AI功能将不可用")
    
    # 验证OpenClaw配置
    if config.openclaw.enabled:
        if not config.openclaw.token:
            errors.append("OPENCLAW_TOKEN 未配置（OpenClaw HTTP API需要）")
        if not config.openclaw.gateway_url:
            errors.append("OPENCLAW_GATEWAY_URL 未配置")
    
    # 验证工作目录
    if not os.path.exists(config.workspace_dir):
        try:
            os.makedirs(config.workspace_dir, exist_ok=True)
        except Exception as e:
            errors.append(f"工作目录无法创建: {str(e)}")
    
    return len(errors) == 0, errors


def get_ai_config_dict(config: AIConfig) -> Dict[str, Any]:
    """获取AI配置字典（兼容旧代码）
    
    Args:
        config: AI配置对象
        
    Returns:
        AI配置字典
    """
    return {
        'AI_PROVIDER': config.provider,
        'AI_API_KEY': config.api_key,
        'AI_API_BASE': config.api_base,
        'AI_MODEL_NAME': config.model_name,
        'AI_TIMEOUT': config.timeout,
        'AI_MAX_RETRIES': config.max_retries
    }
