"""OpenClaw 桥接模块

通过 HTTP API 与 OpenClaw 网关通信，用于私聊消息处理。
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class OpenClawBridge:
    """OpenClaw 桥接器
    
    通过 HTTP API 与同服务器上的 OpenClaw 网关通信。
    支持多种 API 端点的自动探测。
    """
    
    def __init__(
        self,
        gateway_url: str = "http://localhost:18789",
        token: str = "",
        agent_id: str = "main",
        timeout: int = 90
    ):
        self.gateway_url = gateway_url.rstrip('/')
        self.token = token
        self.agent_id = agent_id
        self.timeout = timeout
        
        logger.info(f"OpenClaw 桥接器初始化 - 网关: {self.gateway_url}")
    
    def send_message(
        self,
        user_message: str,
        user_id: str,
        user_name: str = "用户",
        chat_id: str = "",
        message_id: str = ""
    ) -> Dict[str, Any]:
        """发送消息到 OpenClaw 处理"""
        logger.info(f"发送消息到 OpenClaw: user={user_name}, message={user_message[:50]}...")
        
        # 策略：尝试多种可能的 API 端点
        strategies = [
            self._try_rpc_api,
            self._try_webhook_api,
            self._try_message_api,
            self._try_chat_api
        ]
        
        for strategy in strategies:
            result = strategy(user_message, user_id, user_name, chat_id, message_id)
            if result.get("success"):
                return result
        
        logger.warning("所有 OpenClaw API 调用策略都失败")
        return {
            "success": False,
            "error": "无法连接到 OpenClaw 服务",
            "result": self._build_error_message()
        }
    
    def _make_request(
        self,
        url: str,
        payload: Dict[str, Any],
        method: str = "POST"
    ) -> Optional[requests.Response]:
        """执行 HTTP 请求的通用方法
        
        Args:
            url: 请求地址
            payload: 请求体
            method: 请求方法 (GET/POST)
            
        Returns:
            成功返回 Response 对象，失败返回 None
        """
        try:
            headers = self._build_headers()
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            else:
                response = requests.post(
                    url, json=payload, headers=headers, timeout=self.timeout
                )
            
            if response.status_code in [200, 201]:
                return response
            
            logger.debug(f"请求返回非成功状态码: {response.status_code}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.debug(f"请求失败: {str(e)}")
            return None
    
    def _process_response(self, response: requests.Response, api_name: str) -> Dict[str, Any]:
        """处理成功响应的通用方法
        
        Args:
            response: HTTP 响应
            api_name: API 名称（用于日志）
            
        Returns:
            处理结果字典
        """
        logger.info(f"✅ OpenClaw {api_name} 调用成功")
        
        try:
            result = response.json()
            reply = self._extract_reply(result)
        except (json.JSONDecodeError, ValueError):
            reply = response.text
            result = {"text": response.text}
        
        return {
            "success": True,
            "result": reply,
            "raw_response": result
        }
    
    def _try_endpoints(
        self,
        endpoints: List[str],
        payload: Dict[str, Any],
        api_name: str
    ) -> Dict[str, Any]:
        """尝试多个端点的通用方法
        
        Args:
            endpoints: 端点列表
            payload: 请求体
            api_name: API 名称
            
        Returns:
            成功结果或 {"success": False}
        """
        for endpoint in endpoints:
            url = f"{self.gateway_url}{endpoint}"
            response = self._make_request(url, payload)
            
            if response:
                logger.info(f"✅ OpenClaw {api_name} 调用成功: {endpoint}")
                return self._process_response(response, api_name)
        
        return {"success": False}
    
    def _try_rpc_api(
        self, message: str, user_id: str, user_name: str,
        chat_id: str, message_id: str
    ) -> Dict[str, Any]:
        """尝试使用 RPC API"""
        payload = {
            "jsonrpc": "2.0",
            "method": "processMessage",
            "params": {
                "message": message,
                "userId": user_id,
                "userName": user_name,
                "chatId": chat_id,
                "messageId": message_id,
                "channel": "feishu",
                "agentId": self.agent_id
            },
            "id": 1
        }
        
        return self._try_endpoints(["/rpc"], payload, "RPC API")
    
    def _try_webhook_api(
        self, message: str, user_id: str, user_name: str,
        chat_id: str, message_id: str
    ) -> Dict[str, Any]:
        """尝试使用 Webhook API"""
        payload = {
            "schema": "2.0",
            "header": {
                "event_type": "im.message.receive_v1",
                "event_id": message_id
            },
            "event": {
                "sender": {
                    "sender_id": {
                        "open_id": user_id,
                        "user_id": user_name
                    }
                },
                "message": {
                    "message_id": message_id,
                    "chat_id": chat_id,
                    "chat_type": "p2p",
                    "content": json.dumps({"text": message})
                }
            }
        }
        
        endpoints = ["/webhook", "/api/webhook", "/webhooks"]
        return self._try_endpoints(endpoints, payload, "Webhook API")
    
    def _try_message_api(
        self, message: str, user_id: str, user_name: str,
        chat_id: str, message_id: str
    ) -> Dict[str, Any]:
        """尝试使用 Message API"""
        endpoints = ["/api/messages", "/messages", "/api/message"]
        
        # 尝试多种请求格式
        payloads = [
            {
                "message": message,
                "userId": user_id,
                "userName": user_name,
                "chatId": chat_id,
                "messageId": message_id,
                "channel": "feishu",
                "agentId": self.agent_id
            },
            {"text": message, "user": user_id, "channel": "feishu"},
            {"message": message, "user": user_id}
        ]
        
        for endpoint in endpoints:
            for payload in payloads:
                url = f"{self.gateway_url}{endpoint}"
                response = self._make_request(url, payload)
                
                if response:
                    logger.info(f"✅ OpenClaw Message API 调用成功: {endpoint}")
                    return self._process_response(response, "Message API")
        
        return {"success": False}
    
    def _try_chat_api(
        self, message: str, user_id: str, user_name: str,
        chat_id: str, message_id: str
    ) -> Dict[str, Any]:
        """尝试使用 Chat API"""
        payload = {
            "messages": [{"role": "user", "content": message}],
            "user": user_id,
            "metadata": {
                "userName": user_name,
                "chatId": chat_id,
                "messageId": message_id,
                "channel": "feishu",
                "agentId": self.agent_id
            }
        }
        
        endpoints = ["/api/chat", "/chat", "/v1/chat/completions"]
        return self._try_endpoints(endpoints, payload, "Chat API")
    
    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "FeishuBot/1.1.0"
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        return headers
    
    def _extract_reply(self, response_data: Any) -> str:
        """从响应中提取回复内容"""
        if isinstance(response_data, str):
            return response_data
        
        if isinstance(response_data, dict):
            possible_fields = [
                "reply", "response", "result", "message", "content", "text",
                "data.reply", "data.response", "data.message",
                "choices.0.message.content"
            ]
            
            for field in possible_fields:
                value = self._get_nested_value(response_data, field)
                if value:
                    return str(value)
        
        return json.dumps(response_data, ensure_ascii=False, indent=2)
    
    def _get_nested_value(self, data: dict, path: str) -> Any:
        """获取嵌套字典的值"""
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(value):
                    value = value[index]
                else:
                    return None
            else:
                return None
        
        return value
    
    def _build_error_message(self) -> str:
        """构建错误提示消息"""
        return """⚠️ OpenClaw 服务暂时不可用

请检查：
1. OpenClaw 网关是否运行
2. 网关地址是否正确
3. 网络连接是否正常

管理员请查看服务器日志获取详细信息。"""
    
    def health_check(self) -> Dict[str, Any]:
        """检查 OpenClaw 网关健康状态"""
        endpoints = ["/health", "/status", "/api/health", "/api/status", "/"]
        
        for endpoint in endpoints:
            url = f"{self.gateway_url}{endpoint}"
            response = self._make_request(url, {}, method="GET")
            
            if response:
                logger.info(f"✅ OpenClaw 健康检查通过: {endpoint}")
                return {
                    "healthy": True,
                    "status_code": response.status_code,
                    "endpoint": endpoint,
                    "gateway_url": self.gateway_url
                }
        
        return {
            "healthy": False,
            "error": "无法访问任何健康检查端点",
            "gateway_url": self.gateway_url
        }


def create_openclaw_bridge(
    gateway_url: str = "http://localhost:18789",
    token: str = "",
    agent_id: str = "main",
    timeout: int = 90
) -> OpenClawBridge:
    """创建 OpenClaw 桥接器实例"""
    return OpenClawBridge(
        gateway_url=gateway_url,
        token=token,
        agent_id=agent_id,
        timeout=timeout
    )
