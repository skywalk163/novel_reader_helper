#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI API客户端模块
提供OpenAI兼容的AI模型API调用功能
"""

import json
import time
import requests
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
from ai_config import AIModelConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """聊天消息数据类"""
    role: str  # system, user, assistant
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {"role": self.role, "content": self.content}

@dataclass
class APIResponse:
    """API响应数据类"""
    success: bool
    content: str
    model: str
    usage: Dict[str, int]
    error_message: str = ""
    error_code: str = ""
    response_time: float = 0.0

class AIApiClient:
    """AI API客户端，支持OpenAI兼容的API"""
    
    def __init__(self, model_config: AIModelConfig, timeout: int = 30, max_retries: int = 3):
        """初始化AI API客户端
        
        Args:
            model_config: AI模型配置
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.model_config = model_config
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {model_config.token_key}',
            'User-Agent': 'NovelReaderHelper/1.0'
        })
        
        # 增加超时时间设置
        self.timeout = max(timeout, 120)  # 最少120秒
        self.max_retries = max_retries
        
        # API端点
        self.chat_url = f"{model_config.base_url.rstrip('/')}/chat/completions"
        self.models_url = f"{model_config.base_url.rstrip('/')}/models"
    
    def test_connection(self) -> APIResponse:
        """测试API连接
        
        Returns:
            连接测试结果
        """
        try:
            # 尝试获取可用模型列表（某些API可能不支持）
            start_time = time.time()
            response = self.session.get(self.models_url, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return APIResponse(
                    success=True,
                    content="连接成功",
                    model=self.model_config.model_name,
                    usage={},
                    response_time=response_time
                )
            else:
                # 如果获取模型列表失败，尝试发送一个简单的聊天请求
                return self._test_simple_chat()
                
        except Exception as e:
            # 如果获取模型列表失败，尝试发送一个简单的聊天请求
            return self._test_simple_chat()
    
    def _test_simple_chat(self) -> APIResponse:
        """通过简单聊天请求测试连接"""
        try:
            messages = [
                ChatMessage(role="user", content="Hello").to_dict()
            ]
            
            response = self._make_request(messages, max_tokens=10)
            
            if response.success:
                response.content = "连接成功"
                response.error_message = ""
            
            return response
            
        except Exception as e:
            return APIResponse(
                success=False,
                content="",
                model="",
                usage={},
                error_message=f"连接测试失败: {str(e)}",
                response_time=0.0
            )
    
    def generate_summary(self, text: str, max_tokens: int = 500) -> APIResponse:
        """生成文本总结
        
        Args:
            text: 要总结的文本
            max_tokens: 最大生成token数
            
        Returns:
            总结结果
        """
        # 构建专门用于文本总结的prompt
        system_prompt = """你是一个专业的小说内容分析师。请对提供的小说章节内容进行总结，要求：
1. 提取主要情节和关键信息
2. 总结要简洁明了，控制在3-5句话内
3. 重点关注故事发展和重要事件
4. 不要添加原书中没有的内容
5. 使用客观中性的语气进行总结"""

        user_prompt = f"请总结以下小说章节内容：\n\n{text}"
        
        messages = [
            ChatMessage(role="system", content=system_prompt).to_dict(),
            ChatMessage(role="user", content=user_prompt).to_dict()
        ]
        
        return self._make_request(messages, max_tokens=max_tokens)
    
    def generate_analysis(self, text: str, analysis_type: str = "comprehensive") -> APIResponse:
        """生成文本分析
        
        Args:
            text: 要分析的文本
            analysis_type: 分析类型 (comprehensive, characters, plot, themes)
            
        Returns:
            分析结果
        """
        if analysis_type == "characters":
            system_prompt = "你是一个专业的文学分析师。请分析以下文本中出现的角色，包括他们的特征、行为和相互关系。"
        elif analysis_type == "plot":
            system_prompt = "你是一个专业的文学分析师。请分析以下文本的情节发展，包括起承转合和关键事件。"
        elif analysis_type == "themes":
            system_prompt = "你是一个专业的文学分析师。请分析以下文本的主题和思想内容，包括其中蕴含的深层含义。"
        else:
            system_prompt = """你是一个专业的文学分析师。请对以下小说章节进行全面分析，包括：
1. 情节发展和关键事件
2. 主要角色及其特征
3. 主题思想和情感基调
4. 文学手法和写作特点"""

        user_prompt = f"请分析以下小说章节内容：\n\n{text}"
        
        messages = [
            ChatMessage(role="system", content=system_prompt).to_dict(),
            ChatMessage(role="user", content=user_prompt).to_dict()
        ]
        
        return self._make_request(messages, max_tokens=800)
    
    def _make_request(self, messages: List[Dict], max_tokens: int = 500, temperature: float = 0.7) -> APIResponse:
        """发送API请求
        
        Args:
            messages: 消息列表
            max_tokens: 最大生成token数
            temperature: 温度参数
            
        Returns:
            API响应结果
        """
        request_data = {
            "model": self.model_config.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        last_error = None
        response_time = 0.0
        
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                logger.info(f"发送API请求 (尝试 {attempt + 1}/{self.max_retries + 1}): {self.chat_url}")
                
                response = self.session.post(
                    self.chat_url,
                    json=request_data,
                    timeout=self.timeout
                )
                
                response_time = time.time() - start_time
                
                logger.info(f"API响应状态码: {response.status_code}, 响应时间: {response_time:.2f}秒")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        
                        # 解析响应
                        choices = result.get('choices', [])
                        if not choices:
                            return APIResponse(
                                success=False,
                                content="",
                                model="",
                                usage={},
                                error_message="API响应中没有choices字段",
                                error_code="INVALID_RESPONSE",
                                response_time=response_time
                            )
                        
                        message = choices[0].get('message', {})
                        content = message.get('content', '').strip()
                        
                        if not content:
                            return APIResponse(
                                success=False,
                                content="",
                                model="",
                                usage={},
                                error_message="API返回的内容为空",
                                error_code="EMPTY_CONTENT",
                                response_time=response_time
                            )
                        
                        usage = result.get('usage', {})
                        model = result.get('model', self.model_config.model_name)
                        
                        logger.info(f"API调用成功，生成 {len(content)} 字符")
                        
                        return APIResponse(
                            success=True,
                            content=content,
                            model=model,
                            usage=usage,
                            response_time=response_time
                        )
                        
                    except json.JSONDecodeError as e:
                        last_error = f"解析API响应JSON失败: {e}"
                        logger.error(last_error)
                        break
                else:
                    # 处理HTTP错误
                    error_text = ""
                    try:
                        error_data = response.json()
                        error_text = error_data.get('error', {}).get('message', '')
                        if not error_text:
                            error_text = str(error_data)
                    except (json.JSONDecodeError, ValueError):
                        error_text = response.text
                    
                    error_message = f"HTTP {response.status_code}: {error_text}"
                    last_error = error_message
                    
                    logger.warning(f"API请求失败 (尝试 {attempt + 1}): {error_message}")
                    
                    # 如果是认证错误，不需要重试
                    if response.status_code in [401, 403]:
                        break
                    
                    # 如果是客户端错误，重试意义不大
                    if 400 <= response.status_code < 500 and response.status_code != 429:
                        break
                    
                    # 如果是服务器错误或限流，可以重试
                    if attempt < self.max_retries:
                        wait_time = (2 ** attempt)  # 指数退避
                        logger.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                
            except requests.exceptions.Timeout:
                last_error = f"请求超时 (>{self.timeout}秒)"
                logger.warning(f"API请求超时 (尝试 {attempt + 1})")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                
            except requests.exceptions.ConnectionError:
                last_error = "网络连接错误"
                logger.warning(f"网络连接错误 (尝试 {attempt + 1})")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                
            except Exception as e:
                last_error = f"未知错误: {str(e)}"
                logger.error(f"API请求异常 (尝试 {attempt + 1}): {e}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
        
        # 所有重试都失败了
        return APIResponse(
            success=False,
            content="",
            model="",
            usage={},
            error_message=last_error or "请求失败",
            error_code="REQUEST_FAILED",
            response_time=response_time
        )
    
    def close(self):
        """关闭客户端，清理资源"""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

class AIModelManager:
    """AI模型管理器，统一管理多个AI模型的调用"""
    
    @staticmethod
    def create_client(model_config: AIModelConfig) -> AIApiClient:
        """创建AI客户端
        
        Args:
            model_config: AI模型配置
            
        Returns:
            AI API客户端
        """
        return AIApiClient(model_config)
    
    @staticmethod
    def test_model(model_config: AIModelConfig) -> APIResponse:
        """测试模型连接
        
        Args:
            model_config: AI模型配置
            
        Returns:
            测试结果
        """
        with AIModelManager.create_client(model_config) as client:
            return client.test_connection()
    
    @staticmethod
    def generate_summary(model_config: AIModelConfig, text: str, max_tokens: int = 500) -> APIResponse:
        """使用指定模型生成总结
        
        Args:
            model_config: AI模型配置
            text: 要总结的文本
            max_tokens: 最大生成token数
            
        Returns:
            总结结果
        """
        with AIModelManager.create_client(model_config) as client:
            return client.generate_summary(text, max_tokens)
    
    @staticmethod
    def generate_analysis(model_config: AIModelConfig, text: str, analysis_type: str = "comprehensive") -> APIResponse:
        """使用指定模型生成分析
        
        Args:
            model_config: AI模型配置
            text: 要分析的文本
            analysis_type: 分析类型
            
        Returns:
            分析结果
        """
        with AIModelManager.create_client(model_config) as client:
            return client.generate_analysis(text, analysis_type)

if __name__ == "__main__":
    # 测试代码
    from ai_config import AIModelConfig
    import uuid
    
    # 创建测试配置
    test_config = AIModelConfig(
        id=str(uuid.uuid4()),
        name="测试模型",
        base_url="https://api.openai.com/v1",
        token_key="your-api-key-here",  # 请替换为实际的API密钥
        model_name="gpt-3.5-turbo",
        is_default=True
    )
    
    # 测试连接
    print("测试API连接...")
    test_result = AIModelManager.test_model(test_config)
    
    if test_result.success:
        print(f"✅ 连接成功！响应时间: {test_result.response_time:.2f}秒")
    else:
        print(f"❌ 连接失败: {test_result.error_message}")
        exit(1)
    
    # 测试总结功能
    test_text = """
    张无忌自从学会了乾坤大挪移和太极拳，武功大进，现在终于可以为父母报仇了。
    他来到了光明顶，看到了阳顶天留下的七个字"光明正大，洗刷污垢"，心中感慨万千。
    这时，赵敏带着一群蒙古兵闯了进来，张无忌立即迎上前去，二人战在一处。
    赵敏出招狠辣，张无忌则招招相让，不愿伤她。
    战了几十招，张无忌以乾坤大挪移化解了赵敏的招式，并点中了她的穴道。
    "张教主，你为何不杀我？"赵敏问道。
    张无忌叹了口气："我与姑娘无冤无仇，又怎会取你性命？"
    赵敏心中感动，从此对张无忌芳心暗许。
    """
    
    print("\n测试文本总结功能...")
    summary_result = AIModelManager.generate_summary(test_config, test_text)
    
    if summary_result.success:
        print("✅ 总结成功！")
        print(f"总结内容: {summary_result.content}")
        print(f"使用模型: {summary_result.model}")
        print(f"Token使用: {summary_result.usage}")
        print(f"响应时间: {summary_result.response_time:.2f}秒")
    else:
        print(f"❌ 总结失败: {summary_result.error_message}")
    
    print("\n测试完成！")
