"""OpenClaw桥接器单元测试"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import requests

from feishu_ai_bot.openclaw.bridge import OpenClawBridge, create_openclaw_bridge


@pytest.mark.unit
class TestOpenClawBridge:
    """测试 OpenClawBridge 类"""
    
    def test_init(self):
        """测试初始化"""
        bridge = OpenClawBridge(
            gateway_url="http://localhost:18789",
            token="test-token",
            agent_id="test-agent"
        )
        assert bridge.gateway_url == "http://localhost:18789"
        assert bridge.token == "test-token"
        assert bridge.agent_id == "test-agent"
        assert bridge.timeout == 90
    
    def test_send_message_success(self):
        """测试成功发送消息"""
        bridge = OpenClawBridge(
            gateway_url="http://localhost:18789",
            token="test-token"
        )
        
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "这是测试回复"
                    }
                }
            ]
        }
        
        with patch('requests.post', return_value=mock_response):
            result = bridge.send_message(
                user_message="测试消息",
                user_id="test-user-id"
            )
        
        assert result["success"] is True
        assert result["result"] == "这是测试回复"
    
    def test_send_message_api_error(self):
        """测试 API 返回错误"""
        bridge = OpenClawBridge(
            gateway_url="http://localhost:18789",
            token="test-token"
        )
        
        # 模拟 401 错误
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with patch('requests.post', return_value=mock_response):
            result = bridge.send_message(
                user_message="测试消息",
                user_id="test-user-id"
            )
        
        assert result["success"] is False
        assert "认证失败" in result["result"]
    
    def test_send_message_connection_error(self):
        """测试连接错误"""
        bridge = OpenClawBridge(
            gateway_url="http://localhost:18789",
            token="test-token"
        )
        
        with patch('requests.post', side_effect=requests.exceptions.ConnectionError()):
            result = bridge.send_message(
                user_message="测试消息",
                user_id="test-user-id"
            )
        
        assert result["success"] is False
        assert "无法连接" in result["result"]
    
    def test_send_message_timeout(self):
        """测试超时"""
        bridge = OpenClawBridge(
            gateway_url="http://localhost:18789",
            token="test-token"
        )
        
        with patch('requests.post', side_effect=requests.exceptions.Timeout()):
            result = bridge.send_message(
                user_message="测试消息",
                user_id="test-user-id"
            )
        
        assert result["success"] is False
        assert "超时" in result["result"]
    
    def test_health_check_success(self):
        """测试健康检查成功"""
        bridge = OpenClawBridge(
            gateway_url="http://localhost:18789",
            token="test-token"
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        
        with patch('requests.get', return_value=mock_response):
            result = bridge.health_check()
        
        assert result["healthy"] is True
    
    def test_health_check_failure(self):
        """测试健康检查失败"""
        bridge = OpenClawBridge(
            gateway_url="http://localhost:18789",
            token="test-token"
        )
        
        with patch('requests.get', side_effect=requests.exceptions.ConnectionError()):
            result = bridge.health_check()
        
        assert result["healthy"] is False


@pytest.mark.unit
def test_create_openclaw_bridge():
    """测试工厂函数"""
    bridge = create_openclaw_bridge(
        gateway_url="http://test:18789",
        token="test-token"
    )
    assert isinstance(bridge, OpenClawBridge)
    assert bridge.gateway_url == "http://test:18789"
