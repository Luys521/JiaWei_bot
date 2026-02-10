"""任务处理模块

提供任务分类和异步处理功能
"""

import re
import logging
from threading import Thread
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from feishu_ai_bot.bot.feishu import FeishuBot
    from feishu_ai_bot.ai.processor import AITaskProcessor

from feishu_ai_bot.cards.builder import (
    create_simple_response_card,
    create_thread_header_card,
    create_progress_card
)
from feishu_ai_bot.monitoring.stats import increment_tasks_processed

logger = logging.getLogger(__name__)


def is_complex_task(task_description: str) -> bool:
    """判断任务是否为复杂任务
    
    Args:
        task_description: 任务描述
        
    Returns:
        是否为复杂任务
    """
    complex_keywords = [
        "搜索", "查找", "分析", "统计", "计算", "生成", "创建", "编写",
        "执行", "运行", "处理", "转换", "提取", "汇总", "对比", "评估",
        "search", "analyze", "calculate", "generate", "create", "execute",
        "process", "extract", "summarize", "compare", "evaluate"
    ]
    
    # 检查关键词
    for keyword in complex_keywords:
        if keyword in task_description:
            return True
    
    # 检查文本长度
    if len(task_description) > 50:
        return True
    
    # 检查句子数量
    sentence_count = len(re.findall(r'[。！？\.\!\?]', task_description))
    if sentence_count >= 2:
        return True
    
    return False


def process_simple_task(
    task_description: str,
    chat_id: str,
    user_name: str,
    bot: "FeishuBot",
    ai_processor: "AITaskProcessor"
) -> None:
    """处理简单任务（直接回复）
    
    Args:
        task_description: 任务描述
        chat_id: 群聊ID
        user_name: 用户名
        bot: 飞书机器人实例
        ai_processor: AI处理器实例
    """
    try:
        logger.info(f"处理简单任务: {task_description}")
        
        user_info = {"name": user_name, "open_id": ""}
        result = ai_processor.process_task(task_description, user_info)
        
        if result.get("success"):
            response_text = result.get("result", "处理完成，但没有返回结果")
            logger.info(f"AI处理成功: {task_description}")
        else:
            response_text = f"❌ 处理失败: {result.get('error', '未知错误')}"
            logger.error(f"AI处理失败: {result.get('error')}")
        
        # 发送回复卡片
        card = create_simple_response_card(task_description, response_text)
        bot.send_card_message(chat_id, card)
        
        logger.info("简单任务处理完成")
        
    except Exception as e:
        logger.error(f"简单任务处理失败: {str(e)}", exc_info=True)
        bot.send_message(chat_id, f"❌ 处理失败：{str(e)}")


def process_complex_task(
    task_description: str,
    chat_id: str,
    user_name: str,
    message_id: str,
    user_open_id: str,
    bot: "FeishuBot",
    ai_processor: "AITaskProcessor"
) -> None:
    """处理复杂任务（创建话题）
    
    Args:
        task_description: 任务描述
        chat_id: 群聊ID
        user_name: 用户名
        message_id: 消息ID
        user_open_id: 用户Open ID
        bot: 飞书机器人实例
        ai_processor: AI处理器实例
    """
    thread_id: Optional[str] = None
    
    try:
        logger.info(f"处理复杂任务: {task_description}")
        
        # 1. 创建话题
        header_card = create_thread_header_card(task_description, user_name)
        thread_result = bot.reply_message(
            message_id,
            header_card,
            msg_type="interactive",
            reply_in_thread=True
        )
        
        if not thread_result or not thread_result.get("thread_id"):
            logger.error("创建话题失败")
            bot.send_message(chat_id, "❌ 创建任务话题失败")
            return
        
        thread_id = thread_result["thread_id"]
        logger.info(f"话题创建成功: {thread_id}")
        
        # 2. 发送处理中状态
        progress_card = create_progress_card("processing", "正在分析任务需求...")
        bot.send_card_message(chat_id, progress_card, root_id=thread_id)
        
        # 3. 处理任务
        user_info = {"name": user_name, "open_id": user_open_id}
        result = ai_processor.process_task(task_description, user_info)
        
        if result.get("success"):
            result_content = result.get("result", "处理完成，但没有返回结果")
            increment_tasks_processed()
            logger.info(f"AI处理成功: {task_description}")
        else:
            result_content = f"❌ 处理失败: {result.get('error', '未知错误')}"
            logger.error(f"AI处理失败: {result.get('error')}")
        
        # 4. 发送结果
        result_card = create_progress_card("completed", result_content)
        bot.send_card_message(chat_id, result_card, root_id=thread_id)
        
        logger.info("复杂任务处理完成")
        
    except Exception as e:
        logger.error(f"复杂任务处理失败: {str(e)}", exc_info=True)
        error_card = create_progress_card("error", f"错误信息：\n```\n{str(e)}\n```")
        if thread_id:
            bot.send_card_message(chat_id, error_card, root_id=thread_id)
        else:
            bot.send_message(chat_id, f"❌ 处理失败：{str(e)}")


def handle_task_async(
    task_type: str,
    task_description: str,
    chat_id: str,
    user_name: str,
    message_id: str,
    user_open_id: str,
    bot: "FeishuBot",
    ai_processor: "AITaskProcessor"
) -> None:
    """异步处理任务
    
    Args:
        task_type: 任务类型（simple/complex）
        task_description: 任务描述
        chat_id: 群聊ID
        user_name: 用户名
        message_id: 消息ID
        user_open_id: 用户Open ID
        bot: 飞书机器人实例
        ai_processor: AI处理器实例
    """
    if task_type == "complex":
        thread = Thread(
            target=process_complex_task,
            args=(
                task_description, chat_id, user_name,
                message_id, user_open_id, bot, ai_processor
            )
        )
    else:
        thread = Thread(
            target=process_simple_task,
            args=(task_description, chat_id, user_name, bot, ai_processor)
        )
    
    thread.daemon = True
    thread.start()


class TaskProcessor:
    """任务处理器类
    
    提供更灵活的任务处理方式
    """
    
    def __init__(
        self,
        bot: "FeishuBot",
        ai_processor: "AITaskProcessor"
    ):
        """初始化任务处理器
        
        Args:
            bot: 飞书机器人实例
            ai_processor: AI处理器实例
        """
        self.bot = bot
        self.ai_processor = ai_processor
    
    def is_complex(self, task_description: str) -> bool:
        """判断是否为复杂任务"""
        return is_complex_task(task_description)
    
    def process_simple(
        self,
        task_description: str,
        chat_id: str,
        user_name: str
    ) -> None:
        """处理简单任务"""
        process_simple_task(
            task_description, chat_id, user_name,
            self.bot, self.ai_processor
        )
    
    def process_complex(
        self,
        task_description: str,
        chat_id: str,
        user_name: str,
        message_id: str,
        user_open_id: str
    ) -> None:
        """处理复杂任务"""
        process_complex_task(
            task_description, chat_id, user_name,
            message_id, user_open_id, self.bot, self.ai_processor
        )
    
    def process_async(
        self,
        task_type: str,
        task_description: str,
        chat_id: str,
        user_name: str,
        message_id: str,
        user_open_id: str
    ) -> None:
        """异步处理任务"""
        handle_task_async(
            task_type, task_description, chat_id, user_name,
            message_id, user_open_id, self.bot, self.ai_processor
        )
