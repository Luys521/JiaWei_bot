"""飞书卡片构建器模块"""

import json
import time
from typing import Any, Dict


def create_simple_response_card(task_description: str, result: str) -> str:
    """创建简单问答的卡片
    
    Args:
        task_description: 任务描述
        result: 处理结果
        
    Returns:
        卡片JSON字符串
    """
    card: Dict[str, Any] = {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": "blue",
            "title": {"content": "💬 快速回复", "tag": "plain_text"}
        },
        "elements": [
            {
                "tag": "markdown",
                "content": f"**问题：** {task_description}\n\n**回答：**\n{result}"
            }
        ]
    }
    return json.dumps(card)


def create_thread_header_card(task_description: str, user_name: str) -> str:
    """创建话题头部卡片
    
    Args:
        task_description: 任务描述
        user_name: 用户名
        
    Returns:
        卡片JSON字符串
    """
    card: Dict[str, Any] = {
        "config": {"wide_screen_mode": True, "enable_forward": True},
        "header": {
            "template": "turquoise",
            "title": {"content": "📋 任务处理", "tag": "plain_text"}
        },
        "elements": [
            {
                "tag": "markdown",
                "content": f"**任务内容：**\n{task_description}"
            },
            {
                "tag": "hr"
            },
            {
                "tag": "column_set",
                "flex_mode": "none",
                "columns": [
                    {
                        "tag": "column",
                        "width": "weighted",
                        "weight": 1,
                        "elements": [{
                            "tag": "markdown",
                            "content": f"**👤 发起人**\n{user_name}"
                        }]
                    },
                    {
                        "tag": "column",
                        "width": "weighted",
                        "weight": 1,
                        "elements": [{
                            "tag": "markdown",
                            "content": f"**⏰ 创建时间**\n{time.strftime('%Y-%m-%d %H:%M:%S')}"
                        }]
                    }
                ]
            },
            {
                "tag": "hr"
            },
            {
                "tag": "note",
                "elements": [{
                    "tag": "plain_text",
                    "content": "🤖 任务处理进展将在话题中更新，点击查看详情"
                }]
            }
        ]
    }
    return json.dumps(card)


def create_progress_card(status: str, message: str) -> str:
    """创建进度卡片
    
    Args:
        status: 状态 (processing/completed/error)
        message: 消息内容
        
    Returns:
        卡片JSON字符串
    """
    template_map = {
        "processing": {"template": "wathet", "icon": "⏳", "title": "处理中"},
        "completed": {"template": "green", "icon": "✅", "title": "已完成"},
        "error": {"template": "red", "icon": "❌", "title": "处理失败"}
    }
    
    config = template_map.get(status, template_map["processing"])
    
    card: Dict[str, Any] = {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": config["template"],
            "title": {"content": f"{config['icon']} {config['title']}", "tag": "plain_text"}
        },
        "elements": [
            {
                "tag": "markdown",
                "content": message
            }
        ]
    }
    return json.dumps(card)


class CardBuilder:
    """卡片构建器类
    
    提供更灵活的卡片构建方式
    """
    
    @staticmethod
    def simple_response(task: str, result: str) -> str:
        """简单回复卡片"""
        return create_simple_response_card(task, result)
    
    @staticmethod
    def thread_header(task: str, user: str) -> str:
        """话题头部卡片"""
        return create_thread_header_card(task, user)
    
    @staticmethod
    def progress(status: str, message: str) -> str:
        """进度卡片"""
        return create_progress_card(status, message)
