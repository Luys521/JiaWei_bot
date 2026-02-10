"""飞书机器人API交互模块"""

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class FeishuBot:
    """飞书机器人类
    
    提供飞书API交互功能，包括消息发送、回复、签名验证等。
    
    Attributes:
        app_id: 飞书应用ID
        app_secret: 飞书应用密钥
        access_token: 访问令牌（自动刷新）
        token_expire_time: 令牌过期时间
        encrypt_key: 事件加密密钥
        verification_token: 验证令牌
    """
    
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        encrypt_key: str = "",
        verification_token: str = ""
    ):
        """初始化飞书机器人
        
        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
            encrypt_key: 事件加密密钥（可选）
            verification_token: 验证令牌（可选）
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token: Optional[str] = None
        self.token_expire_time = 0
        self.encrypt_key = encrypt_key
        self.verification_token = verification_token
        
    def get_tenant_access_token(self) -> Optional[str]:
        """获取tenant_access_token
        
        自动管理令牌缓存，在过期前300秒刷新。
        
        Returns:
            访问令牌，失败返回None
        """
        if self.access_token and time.time() < self.token_expire_time:
            return self.access_token
            
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result.get("tenant_access_token")
                # 提前300秒过期，避免边界问题
                self.token_expire_time = time.time() + result.get("expire", 7200) - 300
                logger.info("成功获取tenant_access_token")
                return self.access_token
            else:
                logger.error(f"获取token失败: {result}")
                return None
        except Exception as e:
            logger.error(f"获取token异常: {str(e)}")
            return None
    
    def send_message(
        self,
        chat_id: str,
        content: str,
        msg_type: str = "text",
        root_id: Optional[str] = None,
        reply_in_thread: bool = False
    ) -> Optional[Dict[str, Any]]:
        """发送消息到群聊或话题
        
        Args:
            chat_id: 群聊ID
            content: 消息内容
            msg_type: 消息类型，默认为text
            root_id: 话题根消息ID（可选）
            reply_in_thread: 是否创建话题回复
            
        Returns:
            API响应结果，失败返回None
        """
        token = self.get_tenant_access_token()
        if not token:
            logger.error("无法获取access_token，消息发送失败")
            return None
            
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {"receive_id_type": "chat_id"}
        
        data: Dict[str, Any] = {
            "receive_id": chat_id,
            "msg_type": msg_type,
            "content": json.dumps({"text": content}) if msg_type == "text" else content
        }
        
        # 如果指定了root_id，则回复到话题中
        if root_id:
            data["root_id"] = root_id
        
        # 如果设置reply_in_thread=True，则创建话题
        if reply_in_thread:
            data["reply_in_thread"] = True
        
        try:
            response = requests.post(url, headers=headers, params=params, json=data)
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"消息发送成功: chat_id={chat_id}, msg_type={msg_type}")
                return result
            else:
                logger.error(f"消息发送失败: {result}")
                return None
        except Exception as e:
            logger.error(f"发送消息异常: {str(e)}")
            return None
    
    def send_card_message(
        self,
        chat_id: str,
        card_content: str,
        root_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """发送卡片消息
        
        Args:
            chat_id: 群聊ID
            card_content: 卡片内容（JSON字符串）
            root_id: 话题根消息ID（可选）
            
        Returns:
            API响应结果
        """
        return self.send_message(chat_id, card_content, msg_type="interactive", root_id=root_id)
    
    def reply_message(
        self,
        message_id: str,
        content: str,
        msg_type: str = "text",
        reply_in_thread: bool = False
    ) -> Optional[Dict[str, Any]]:
        """回复消息
        
        Args:
            message_id: 原消息ID
            content: 回复内容
            msg_type: 消息类型
            reply_in_thread: 是否在话题中回复
            
        Returns:
            API响应结果
        """
        token = self.get_tenant_access_token()
        if not token:
            logger.error("无法获取access_token，回复失败")
            return None
            
        url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data: Dict[str, Any] = {
            "msg_type": msg_type,
            "content": json.dumps({"text": content}) if msg_type == "text" else content
        }
        
        if reply_in_thread:
            data["reply_in_thread"] = True
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"回复消息成功: message_id={message_id}")
                return result
            else:
                logger.error(f"回复消息失败: {result}")
                return None
        except Exception as e:
            logger.error(f"回复消息异常: {str(e)}")
            return None
    
    def verify_event_signature(self, data: str, signature: str, timestamp: str) -> bool:
        """验证飞书事件签名
        
        Args:
            data: 事件数据
            signature: 签名
            timestamp: 时间戳
            
        Returns:
            是否验证通过
        """
        if not self.encrypt_key:
            logger.warning("未配置加密密钥，跳过签名验证")
            return True
        
        try:
            # 构建签名字符串
            sign_str = f"{timestamp}{data}"
            
            # 计算签名
            computed_signature = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
            
            # 验证签名
            is_valid = computed_signature == signature
            
            if not is_valid:
                logger.warning(f"签名验证失败: computed={computed_signature}, received={signature}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"签名验证异常: {str(e)}")
            return False
    
    def verify_verification_token(self, token: str) -> bool:
        """验证飞书验证令牌
        
        Args:
            token: 验证令牌
            
        Returns:
            是否验证通过
        """
        if not self.verification_token:
            logger.warning("未配置验证令牌，跳过令牌验证")
            return True
        
        is_valid = token == self.verification_token
        
        if not is_valid:
            logger.warning(f"验证令牌失败: received={token}")
        
        return is_valid
