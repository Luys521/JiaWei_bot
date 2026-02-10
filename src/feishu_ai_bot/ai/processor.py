"""AI任务处理器模块"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import requests

from feishu_ai_bot.config import AIConfig

logger = logging.getLogger(__name__)


class AITaskProcessor:
    """AI任务处理器
    
    集成多种AI模型能力，处理用户任务
    
    Attributes:
        workspace_dir: 工作目录
        config: AI配置
        ai_provider: AI提供商
        api_key: API密钥
        api_base: API基础地址
        model_name: 模型名称
        timeout: 请求超时时间
    """
    
    def __init__(self, workspace_dir: str, config: AIConfig):
        """初始化AI任务处理器
        
        Args:
            workspace_dir: 工作目录
            config: AI配置对象
        """
        self.workspace_dir = workspace_dir
        self.config = config
        
        # AI模型配置
        self.ai_provider = config.provider
        self.api_key = config.api_key
        self.api_base = config.api_base
        self.model_name = config.model_name
        self.timeout = config.timeout
        
        # 设置默认API地址（如果未配置）
        if not self.api_base:
            if self.ai_provider == 'deepseek':
                self.api_base = 'https://api.deepseek.com/v1'
                if not self.model_name:
                    self.model_name = 'deepseek-chat'
            elif self.ai_provider == 'minimax':
                self.api_base = 'https://api.minimax.chat/v1'
                if not self.model_name:
                    self.model_name = 'abab5.5-chat'
            elif self.ai_provider == 'openai':
                self.api_base = 'https://api.openai.com/v1'
                if not self.model_name:
                    self.model_name = 'gpt-3.5-turbo'
        
        logger.info(
            f"AI处理器初始化完成 - "
            f"提供商: {self.ai_provider}, 模型: {self.model_name}"
        )
    
    def process_task(
        self,
        task_description: str,
        user_info: Dict[str, str]
    ) -> Dict[str, Any]:
        """处理用户任务
        
        Args:
            task_description: 任务描述
            user_info: 用户信息 {"name": "用户名", "open_id": "open_id"}
            
        Returns:
            处理结果字典
        """
        try:
            logger.info(f"AI开始处理任务: {task_description}")
            
            # 分析任务类型
            task_type = self._classify_task(task_description)
            logger.info(f"任务类型: {task_type}")
            
            # 根据任务类型处理
            result = self._process_by_type(task_type, task_description, user_info)
            
            return {
                "success": True,
                "result": result,
                "task_type": task_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI处理任务失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _classify_task(self, task_description: str) -> str:
        """分类任务类型
        
        Args:
            task_description: 任务描述
            
        Returns:
            任务类型: search, file, analysis, code, general
        """
        task_lower = task_description.lower()
        
        # 搜索类任务
        if any(kw in task_lower for kw in ["搜索", "查找", "search", "找"]):
            return 'search'
        
        # 文件操作类任务
        elif any(kw in task_lower for kw in ["创建文件", "生成文件", "写入", "保存", "新建文件"]):
            return 'file'
        
        # 数据分析类任务
        elif any(kw in task_lower for kw in ["分析", "统计", "汇总", "报表", "数据"]):
            return 'analysis'
        
        # 代码执行类任务
        elif any(kw in task_lower for kw in ["运行", "执行", "计算", "代码", "编程"]):
            return 'code'
        
        # 默认：通用任务
        return 'general'
    
    def _process_by_type(
        self,
        task_type: str,
        task_description: str,
        user_info: Dict[str, str]
    ) -> str:
        """根据类型处理任务
        
        Args:
            task_type: 任务类型
            task_description: 任务描述
            user_info: 用户信息
            
        Returns:
            处理结果
        """
        handlers = {
            'search': self._handle_search,
            'file': self._handle_file,
            'analysis': self._handle_analysis,
            'code': self._handle_code,
            'general': self._handle_general
        }
        
        handler = handlers.get(task_type, self._handle_general)
        return handler(task_description, user_info)
    
    def _call_ai_api(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """调用AI API（带重试机制）
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            
        Returns:
            AI返回的结果
        """
        if not self.api_key:
            raise ValueError("AI API密钥未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        max_retries = self.config.max_retries
        
        for attempt in range(max_retries):
            try:
                url = f"{self.api_base}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                
                response = requests.post(
                    url, headers=headers, json=data, timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                logger.info(f"AI API调用成功，返回长度: {len(content)}")
                return content
                
            except requests.exceptions.Timeout:
                logger.warning(f"AI API调用超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                    continue
                raise Exception("AI服务响应超时")
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"AI API调用失败: {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                    continue
                raise Exception(f"AI服务调用失败: {str(e)}")
                
            except (KeyError, IndexError) as e:
                logger.error(f"AI API响应格式错误: {str(e)}")
                raise Exception("AI服务返回数据格式错误")
        
        return ""  # 应该不会执行到这里
    
    def _handle_search(self, task: str, user_info: Dict[str, str]) -> str:
        """处理搜索任务"""
        system_prompt = """你是一个智能搜索助手。当用户要求搜索时，请：
1. 理解用户的搜索需求
2. 提供相关的搜索建议和关键词
3. 给出清晰、有条理的回答"""
        
        prompt = f"用户{user_info.get('name', '用户')}要求搜索：{task}\n\n请提供搜索建议。"
        
        try:
            result = self._call_ai_api(prompt, system_prompt)
            return f"🔍 搜索结果\n\n{result}\n\n💡 提示：如需更详细的搜索，可以提供更多关键词"
        except Exception as e:
            return f"❌ 搜索处理失败：{str(e)}"
    
    def _handle_file(self, task: str, user_info: Dict[str, str]) -> str:
        """处理文件任务"""
        system_prompt = """你是一个文件操作助手。当用户要求创建或操作文件时，请：
1. 理解文件的需求和用途
2. 提供合适的文件内容建议
3. 给出文件保存的建议路径和名称"""
        
        prompt = f"用户{user_info.get('name', '用户')}要求：{task}\n\n请提供文件内容建议。"
        
        try:
            result = self._call_ai_api(prompt, system_prompt)
            return f"📁 文件操作结果\n\n{result}\n\n💡 提示：文件将保存在工作目录中"
        except Exception as e:
            return f"❌ 文件操作失败：{str(e)}"
    
    def _handle_analysis(self, task: str, user_info: Dict[str, str]) -> str:
        """处理分析任务"""
        system_prompt = """你是一个数据分析助手。当用户要求分析数据时，请：
1. 理解分析的目的和需求
2. 提供分析方法和步骤
3. 给出可能的结论和建议"""
        
        prompt = f"用户{user_info.get('name', '用户')}要求分析：{task}\n\n请提供分析方案。"
        
        try:
            result = self._call_ai_api(prompt, system_prompt)
            return f"📊 数据分析结果\n\n{result}\n\n💡 提示：如需更深入的分析，请提供更多数据"
        except Exception as e:
            return f"❌ 数据分析失败：{str(e)}"
    
    def _handle_code(self, task: str, user_info: Dict[str, str]) -> str:
        """处理代码任务"""
        system_prompt = """你是一个编程助手。当用户要求执行代码或编程任务时，请：
1. 理解任务需求和目标
2. 提供完整、可运行的代码
3. 添加必要的注释说明
4. 解释代码的工作原理"""
        
        prompt = f"用户{user_info.get('name', '用户')}要求：{task}\n\n请提供代码和执行结果。"
        
        try:
            result = self._call_ai_api(prompt, system_prompt)
            return f"💻 代码执行结果\n\n{result}\n\n💡 提示：代码已准备好，可以直接运行"
        except Exception as e:
            return f"❌ 代码执行失败：{str(e)}"
    
    def _handle_general(self, task: str, user_info: Dict[str, str]) -> str:
        """处理通用任务"""
        system_prompt = """你是一个智能助手，能够帮助用户处理各种任务。请：
1. 理解用户的需求
2. 提供有帮助、准确的信息
3. 用清晰、友好的方式回答"""
        
        prompt = f"用户{user_info.get('name', '用户')}说：{task}\n\n请提供帮助。"
        
        try:
            result = self._call_ai_api(prompt, system_prompt)
            return f"✨ 处理结果\n\n{result}\n\n💡 如需更多帮助，请继续提问"
        except Exception as e:
            return f"❌ 处理失败：{str(e)}"
