"""飞书AI机器人 - 主服务

新架构下的 Flask 主服务入口
"""

import json
import logging
import sys
from pathlib import Path

from flask import Flask, request, jsonify

# 配置日志（在导入其他模块之前）
from feishu_ai_bot.config import load_config

config = load_config()

# 确保日志目录存在
log_path = Path(config.server.log_file)
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, config.server.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.server.log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("🚀 飞书AI机器人服务启动中...")
logger.info(f"版本: {config.version}")
logger.info("=" * 60)

# 导入其他模块
from feishu_ai_bot.bot.feishu import FeishuBot
from feishu_ai_bot.ai.processor import AITaskProcessor
from feishu_ai_bot.tasks.processor import is_complex_task, handle_task_async
from feishu_ai_bot.security.validator import SecurityValidator
from feishu_ai_bot.monitoring.stats import StatsCollector, update_stats
from feishu_ai_bot.openclaw.bridge import create_openclaw_bridge

# 初始化组件
feishu_bot = FeishuBot(
    app_id=config.feishu.app_id,
    app_secret=config.feishu.app_secret,
    encrypt_key=config.feishu.encrypt_key,
    verification_token=config.feishu.verification_token
)

ai_processor = AITaskProcessor(
    workspace_dir=config.workspace_dir,
    config=config.ai
)

security_validator = SecurityValidator(
    rate_limit_per_minute=config.security.rate_limit_per_minute,
    enable_ip_whitelist=config.security.enable_ip_whitelist,
    ip_whitelist=config.security.ip_whitelist,
    enable_event_verification=config.security.enable_event_verification
)

stats_collector = StatsCollector()

# 初始化 OpenClaw 桥接器（可选）
openclaw_bridge = None
if config.openclaw.enabled:
    try:
        logger.info("🔧 正在初始化 OpenClaw 桥接器...")
        openclaw_bridge = create_openclaw_bridge(
            gateway_url=config.openclaw.gateway_url,
            token=config.openclaw.token,
            agent_id=config.openclaw.agent_id,
            timeout=config.openclaw.timeout
        )
        
        # 健康检查
        health = openclaw_bridge.health_check()
        if health.get("healthy"):
            logger.info("✅ OpenClaw 桥接器已启用")
        else:
            logger.warning(f"⚠️ OpenClaw 健康检查失败: {health.get('error')}")
    except Exception as e:
        logger.error(f"❌ OpenClaw 桥接器初始化失败: {str(e)}")
        openclaw_bridge = None

# 创建 Flask 应用
app = Flask(__name__)


@app.route('/webhook/event', methods=['POST'])
def handle_event():
    """处理飞书事件"""
    try:
        # 验证请求格式
        if not request.is_json:
            logger.warning("收到非JSON请求")
            return jsonify({"code": -1, "msg": "Content-Type must be application/json"}), 400
        
        data = request.get_json(silent=True)
        if data is None:
            logger.warning("收到无效的JSON数据")
            return jsonify({"code": -1, "msg": "Invalid JSON"}), 400
        
        # 更新统计
        update_stats()
        
        logger.info(f"收到事件: {json.dumps(data, ensure_ascii=False)[:200]}...")
        
        # 验证挑战请求（飞书首次配置时的验证）
        if "challenge" in data:
            logger.info("收到挑战请求")
            return jsonify({"challenge": data["challenge"]})
        
        # 解析事件数据
        event_type = data.get("header", {}).get("event_type")
        
        if event_type == "im.message.receive_v1":
            return handle_message_event(data)
        else:
            logger.info(f"未处理的事件类型: {event_type}")
            return jsonify({"code": 0, "msg": "Event ignored"})
            
    except Exception as e:
        logger.error(f"处理事件失败: {str(e)}", exc_info=True)
        update_stats(success=False)
        return jsonify({"code": -1, "msg": str(e)}), 500


def handle_message_event(data: dict):
    """处理消息事件"""
    try:
        event = data.get("event", {})
        message = event.get("message", {})
        sender = event.get("sender", {})
        
        # 获取消息信息
        chat_id = message.get("chat_id")
        chat_type = message.get("chat_type")
        message_id = message.get("message_id")
        content = json.loads(message.get("content", "{}"))
        text = content.get("text", "")
        
        # 获取发送者信息
        sender_id = sender.get("sender_id", {})
        user_open_id = sender_id.get("open_id")
        user_name = sender_id.get("user_id", "用户")
        
        # 过滤机器人自己的消息
        if user_open_id == config.feishu.bot_open_id:
            logger.info("忽略自己的消息")
            return jsonify({"code": 0, "msg": "Ignored"})
        
        logger.info(f"收到任务: {text} (来自: {user_name}, 类型: {chat_type})")
        
        # 处理私聊消息
        if chat_type == "p2p":
            return handle_private_message(
                text, chat_id, user_name, user_open_id
            )
        
        # 处理群聊消息
        elif chat_type == "group":
            return handle_group_message(
                text, chat_id, user_name, message_id, user_open_id
            )
        
        else:
            logger.warning(f"未知的聊天类型: {chat_type}")
            return jsonify({"code": 0, "msg": "Unknown chat type"})
            
    except Exception as e:
        logger.error(f"处理消息事件失败: {str(e)}", exc_info=True)
        return jsonify({"code": -1, "msg": str(e)}), 500


def handle_private_message(
    text: str,
    chat_id: str,
    user_name: str,
    user_open_id: str
):
    """处理私聊消息（转发到 OpenClaw）"""
    logger.info("🔀 私聊消息，转发到 OpenClaw 处理")
    
    if not openclaw_bridge:
        logger.error("OpenClaw 桥接器不可用")
        feishu_bot.send_message(
            chat_id,
            "❌ OpenClaw 服务暂时不可用，请稍后重试"
        )
        return jsonify({"code": -1, "msg": "OpenClaw not available"})
    
    try:
        # 发送处理中提示
        feishu_bot.send_message(chat_id, "⏳ 正在处理，请稍候...")
        
        # 调用 OpenClaw
        result = openclaw_bridge.send_message(
            user_message=text,
            user_id=user_open_id,
            user_name=user_name,
            chat_id=chat_id
        )
        
        if result.get("success"):
            response_text = result.get("result", "处理完成")
            logger.info("✅ OpenClaw 处理成功")
            feishu_bot.send_message(chat_id, response_text)
        else:
            error_msg = result.get("error", "未知错误")
            logger.error(f"❌ OpenClaw 处理失败: {error_msg}")
            feishu_bot.send_message(
                chat_id,
                f"❌ 处理失败：{error_msg}"
            )
        
        return jsonify({"code": 0, "msg": "Processed"})
        
    except Exception as e:
        logger.error(f"私聊处理异常: {str(e)}", exc_info=True)
        feishu_bot.send_message(chat_id, f"❌ 处理异常：{str(e)}")
        return jsonify({"code": -1, "msg": str(e)}), 500


def handle_group_message(
    text: str,
    chat_id: str,
    user_name: str,
    message_id: str,
    user_open_id: str
):
    """处理群聊消息"""
    # 检查是否 @ 了机器人
    mentions = json.loads(json.dumps({}))
    if "@_user_1" in text:
        # 移除 @ 标记
        text = text.replace("@_user_1", "").strip()
    
    logger.info(f"💬 群聊消息: {text}")
    
    # 判断任务类型
    if is_complex_task(text):
        logger.info("📋 复杂任务，创建话题处理")
        handle_task_async(
            "complex",
            text,
            chat_id,
            user_name,
            message_id,
            user_open_id,
            feishu_bot,
            ai_processor
        )
    else:
        logger.info("💬 简单任务，直接回复")
        handle_task_async(
            "simple",
            text,
            chat_id,
            user_name,
            message_id,
            user_open_id,
            feishu_bot,
            ai_processor
        )
    
    return jsonify({"code": 0, "msg": "Processing"})


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    health = stats_collector.get_health_status(ai_processor)
    health["openclaw"] = {
        "enabled": config.openclaw.enabled,
        "available": openclaw_bridge is not None
    }
    return jsonify(health)


@app.route('/stats', methods=['GET'])
def get_stats():
    """统计信息端点"""
    stats = stats_collector.get_detailed_stats(ai_processor, config)
    return jsonify(stats)


@app.route('/test/simulate', methods=['POST'])
def test_simulate():
    """模拟飞书事件（仅测试用）"""
    if config.env == "production":
        return jsonify({"code": -1, "msg": "Not available in production"}), 403
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"code": -1, "msg": "Invalid JSON"}), 400
    
    # 构造飞书事件格式
    event_data = {
        "header": {
            "event_type": "im.message.receive_v1"
        },
        "event": {
            "message": {
                "chat_id": data.get("chat_id", "test_chat"),
                "chat_type": data.get("chat_type", "p2p"),
                "message_id": data.get("message_id", "test_msg"),
                "content": json.dumps({"text": data.get("message", "测试消息")})
            },
            "sender": {
                "sender_id": {
                    "open_id": data.get("user_id", "test_user"),
                    "user_id": data.get("user_name", "测试用户")
                }
            }
        }
    }
    
    return handle_message_event(event_data)


@app.route('/test/openclaw', methods=['POST'])
def test_openclaw():
    """测试 OpenClaw 连接"""
    if not openclaw_bridge:
        return jsonify({
            "available": False,
            "error": "OpenClaw 桥接器未初始化"
        })
    
    health = openclaw_bridge.health_check()
    
    if health.get("healthy"):
        # 尝试发送测试消息
        test_result = openclaw_bridge.send_message(
            user_message="Hello",
            user_id="test_user"
        )
        
        return jsonify({
            "available": True,
            "health": health,
            "test_result": test_result.get("success", False)
        })
    else:
        return jsonify({
            "available": False,
            "error": health.get("error", "Unknown error")
        })


def main():
    """主函数"""
    logger.info(f"🚀 启动服务: {config.server.host}:{config.server.port}")
    
    app.run(
        host=config.server.host,
        port=config.server.port,
        debug=config.server.debug
    )


if __name__ == '__main__':
    main()
