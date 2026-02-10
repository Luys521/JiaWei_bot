"""测试配置和共享 fixtures"""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_feishu_bot():
    """模拟飞书机器人"""
    bot = Mock()
    bot.send_message = Mock(return_value={"code": 0})
    bot.send_card_message = Mock(return_value={"code": 0})
    return bot


@pytest.fixture
def mock_openclaw_bridge():
    """模拟 OpenClaw 桥接器"""
    bridge = Mock()
    bridge.send_message = Mock(return_value={
        "success": True,
        "result": "测试回复",
        "raw_response": {}
    })
    bridge.health_check = Mock(return_value={"healthy": True})
    return bridge


@pytest.fixture
def sample_feishu_event():
    """示例飞书事件数据"""
    return {
        "header": {
            "event_id": "test-event-id",
            "event_type": "im.message.receive_v1",
            "create_time": "1234567890"
        },
        "event": {
            "message": {
                "message_id": "test-msg-id",
                "chat_id": "test-chat-id",
                "chat_type": "group",
                "message_type": "text",
                "content": '{"text": "测试消息"}'
            },
            "sender": {
                "sender_id": {
                    "open_id": "test-user-id",
                    "user_id": "test-user"
                }
            }
        }
    }


@pytest.fixture
def sample_private_message_event():
    """示例私聊事件数据"""
    return {
        "header": {
            "event_id": "test-private-event-id",
            "event_type": "im.message.receive_v1"
        },
        "event": {
            "message": {
                "message_id": "test-private-msg-id",
                "chat_id": "test-private-chat-id",
                "chat_type": "p2p",
                "message_type": "text",
                "content": '{"text": "私聊测试消息"}'
            },
            "sender": {
                "sender_id": {
                    "open_id": "test-private-user-id",
                    "user_id": "test-private-user"
                }
            }
        }
    }
