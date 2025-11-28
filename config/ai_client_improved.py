#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的AI API客户端 - 支持流式响应和更好的超时处理
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional, Generator
from dataclasses import dataclass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """聊天消息数据类"""
    role: str
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {
            "role": self.role,
            "content": self.content
        }

@dataclass
class APIResponse:
    """API响应数据类"""
    success: bool
    content: str
    model: str
    usage: Dict[str, Any]
    error_message: str
    error_code: str
    response_time: float

class ImprovedAIClient:
    """改进的AI API客户端"""
    
    def __init__(self, base_url: str, api_key: str, model_name: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model_name = model_name
        self.chat_url = f"{self.base_url}/chat/completions"
        
        # 请求配置
        self.timeout = 120  # 增加到120秒
        self.max_retries = 4
        self.stream_timeout = 180  # 流式响应超时时间
        self.chunk_timeout = 10  # 流数据块之间的最大等待时间
        
        # 创建会话
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def _make_stream_request(self, messages: list, max_tokens: int = 500) -> APIResponse:
        """发起流式API请求"""
        request_data = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": True
        }
        
        response_time = 0.0
        last_error = ""
        
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                logger.info(f"发送流式API请求 (尝试 {attempt + 1}/{self.max_retries + 1}): {self.chat_url}")
                
                response = self.session.post(
                    self.chat_url,
                    json=request_data,
                    timeout=self.timeout,
                    stream=True
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    logger.info(f"流式API连接成功，开始接收数据...")
                    
                    # 处理流式响应
                    content_parts = []
                    usage = {}
                    model = self.model_name
                    
                    last_chunk_time = time.time()
                    
                    try:
                        for line in response.iter_lines(decode_unicode=True):
                            if not line.strip():
                                continue
                            
                            # 更新最后接收数据的时间
                            last_chunk_time = time.time()
                            
                            # 检查是否超时
                            if time.time() - last_chunk_time > self.chunk_timeout:
                                logger.warning("流数据块之间超时，终止接收")
                                break
                            
                            if line.startswith('data: '):
                                data_str = line[6:]  # 移除 'data: ' 前缀
                                
                                if data_str == '[DONE]':
                                    logger.info("流式响应接收完成")
                                    break
                                
                                try:
                                    data = json.loads(data_str)
                                    
                                    if 'choices' in data and data['choices']:
                                        delta = data['choices'][0].get('delta', {})
                                        content_part = delta.get('content', '')
                                        if content_part:
                                            content_parts.append(content_part)
                                    
                                    if 'usage' in data:
                                        usage = data['usage']
                                    
                                    if 'model' in data:
                                        model = data['model']
                                        
                                except json.JSONDecodeError:
                                    continue
                        
                        content = ''.join(content_parts)
                        response_time = time.time() - start_time
                        
                        if content.strip():
                            logger.info(f"流式API调用成功，生成 {len(content)} 字符，响应时间: {response_time:.2f}秒")
                            
                            return APIResponse(
                                success=True,
                                content=content,
                                model=model,
                                usage=usage,
                                error_message="",
                                error_code="",
                                response_time=response_time
                            )
                        else:
                            return APIResponse(
                                success=False,
                                content="",
                                model=model,
                                usage=usage,
                                error_message="流式响应内容为空",
                                error_code="EMPTY_STREAM_CONTENT",
                                response_time=response_time
                            )
                    
                    except Exception as stream_error:
                        logger.error(f"处理流式响应时出错: {stream_error}")
                        last_error = f"流式响应处理错误: {str(stream_error)}"
                        break
                
                else:
                    # HTTP错误
                    error_text = ""
                    try:
                        error_data = response.json()
                        error_text = error_data.get('error', {}).get('message', str(error_data))
                    except (json.JSONDecodeError, ValueError):
                        error_text = response.text
                    
                    error_message = f"HTTP {response.status_code}: {error_text}"
                    last_error = error_message
                    
                    logger.warning(f"流式API请求失败 (尝试 {attempt + 1}): {error_message}")
                    
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
                last_error = f"流式请求超时 (>{self.timeout}秒)"
                logger.warning(f"流式API请求超时 (尝试 {attempt + 1})")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
            
            except Exception as e:
                last_error = f"流式请求异常: {str(e)}"
                logger.error(f"流式API请求异常 (尝试 {attempt + 1}): {e}")
                break
        
        # 所有尝试都失败了
        return APIResponse(
            success=False,
            content="",
            model=self.model_name,
            usage={},
            error_message=last_error,
            error_code="STREAM_REQUEST_FAILED",
            response_time=response_time
        )
    
    def _make_normal_request(self, messages: list, max_tokens: int = 500) -> APIResponse:
        """发起普通API请求（降级方案）"""
        request_data = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": False
        }
        
        response_time = 0.0
        last_error = ""
        
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                logger.info(f"发送普通API请求 (尝试 {attempt + 1}/{self.max_retries + 1}): {self.chat_url}")
                
                response = self.session.post(
                    self.chat_url,
                    json=request_data,
                    timeout=self.timeout
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        
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
                        model = result.get('model', self.model_name)
                        
                        logger.info(f"普通API调用成功，生成 {len(content)} 字符，响应时间: {response_time:.2f}秒")
                        
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
                    # HTTP错误
                    error_text = ""
                    try:
                        error_data = response.json()
                        error_text = error_data.get('error', {}).get('message', str(error_data))
                    except (json.JSONDecodeError, ValueError):
                        error_text = response.text
                    
                    error_message = f"HTTP {response.status_code}: {error_text}"
                    last_error = error_message
                    
                    logger.warning(f"普通API请求失败 (尝试 {attempt + 1}): {error_message}")
                    
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
                logger.warning(f"普通API请求超时 (尝试 {attempt + 1})")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
            
            except Exception as e:
                last_error = f"请求异常: {str(e)}"
                logger.error(f"普通API请求异常 (尝试 {attempt + 1}): {e}")
                break
        
        # 所有尝试都失败了
        return APIResponse(
            success=False,
            content="",
            model=self.model_name,
            usage={},
            error_message=last_error,
            error_code="NORMAL_REQUEST_FAILED",
            response_time=response_time
        )
    
    def generate_summary(self, text: str, max_tokens: int = 500) -> APIResponse:
        """生成文本总结（优先使用流式请求）"""
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
        
        # 优先尝试流式请求
        logger.info("尝试使用流式请求进行总结...")
        result = self._make_stream_request(messages, max_tokens)
        
        # 如果流式请求失败，尝试普通请求
        if not result.success:
            logger.warning("流式请求失败，尝试使用普通请求...")
            result = self._make_normal_request(messages, max_tokens)
        
        return result
    
    def test_connection(self) -> APIResponse:
        """测试连接"""
        messages = [
            ChatMessage(role="user", content="Hello").to_dict()
        ]
        
        response = self._make_stream_request(messages, max_tokens=10)
        
        if response.success:
            response.content = "连接成功"
            response.error_message = ""
        
        return response

# 为了向后兼容，保持原有的类名
class AIModelManager:
    """AI模型管理器（改进版）"""
    
    @staticmethod
    def test_model(model_config) -> APIResponse:
        """测试模型连接"""
        try:
            client = ImprovedAIClient(
                base_url=model_config.base_url,
                api_key=model_config.token_key,
                model_name=model_config.model_name
            )
            
            return client.test_connection()
            
        except Exception as e:
            return APIResponse(
                success=False,
                content="",
                model="",
                usage={},
                error_message=f"连接测试失败: {str(e)}",
                error_code="CONNECTION_TEST_ERROR",
                response_time=0.0
            )
    
    @staticmethod
    def generate_summary(model_config, text: str) -> APIResponse:
        """生成文本总结"""
        try:
            client = ImprovedAIClient(
                base_url=model_config.base_url,
                api_key=model_config.token_key,
                model_name=model_config.model_name
            )
            
            return client.generate_summary(text)
            
        except Exception as e:
            return APIResponse(
                success=False,
                content="",
                model="",
                usage={},
                error_message=f"生成总结失败: {str(e)}",
                error_code="SUMMARY_GENERATION_ERROR",
                response_time=0.0
            )

if __name__ == "__main__":
    # 测试代码
    from config.ai_config import AIModelConfig
    
    # 测试连接
    test_model = AIModelConfig(
        id="test",
        name="测试模型",
        base_url="https://api.openai.com/v1",
        token_key="sk-test",
        model_name="gpt-3.5-turbo"
    )
    
    result = AIModelManager.test_model(test_model)
    print(f"连接测试结果: {result.success}, 错误: {result.error_message}")
