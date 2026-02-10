"""配置模块测试"""

import pytest
import os
from unittest.mock import patch

from feishu_ai_bot.config import (
    FeishuConfig,
    ServerConfig,
    AIConfig,
    OpenClawConfig,
    AppConfig,
    load_config
)


@pytest.mark.unit
class TestConfig:
    """测试配置类"""
    
    def test_feishu_config_defaults(self):
        """测试飞书配置默认值"""
        config = FeishuConfig()
        assert config.app_id == ""
        assert config.app_secret == ""
        assert config.bot_open_id == ""
    
    def test_server_config_defaults(self):
        """测试服务器配置默认值"""
        config = ServerConfig()
        assert config.host == "0.0.0.0"
        assert config.port == 8081
        assert config.log_level == "INFO"
    
    def test_ai_config_defaults(self):
        """测试AI配置默认值"""
        config = AIConfig()
        assert config.provider == "deepseek"
        assert config.timeout == 30
        assert config.max_retries == 3
    
    def test_openclaw_config_defaults(self):
        """测试OpenClaw配置默认值"""
        config = OpenClawConfig()
        assert config.enabled is True
        assert config.gateway_url == "http://localhost:18789"
        assert config.agent_id == "main"
    
    def test_app_config_structure(self):
        """测试应用配置结构"""
        config = AppConfig()
        assert config.name == "feishu-ai-bot"
        assert config.version == "1.1.0"
        assert isinstance(config.feishu, FeishuConfig)
        assert isinstance(config.server, ServerConfig)
        assert isinstance(config.ai, AIConfig)
    
    @patch.dict(os.environ, {
        "FEISHU_APP_ID": "test-app-id",
        "FEISHU_APP_SECRET": "test-secret",
        "SERVER_PORT": "9090",
        "AI_PROVIDER": "openai",
        "OPENCLAW_ENABLED": "false"
    })
    def test_load_config_from_env(self):
        """测试从环境变量加载配置"""
        config = load_config()
        assert config.feishu.app_id == "test-app-id"
        assert config.feishu.app_secret == "test-secret"
        assert config.server.port == 9090
        assert config.ai.provider == "openai"
        assert config.openclaw.enabled is False
    
    @patch.dict(os.environ, {
        "AI_PROVIDER": "deepseek",
        "AI_API_BASE": "",
        "AI_MODEL_NAME": ""
    })
    def test_ai_default_api_base(self):
        """测试AI默认API地址"""
        config = load_config()
        assert config.ai.api_base == "https://api.deepseek.com/v1"
        assert config.ai.model_name == "deepseek-chat"
