"""
LLM Client Base Class

定义 LLM 客户端的抽象基类。
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass


@dataclass
class Message:
    """聊天消息"""
    role: str  # system, user, assistant
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    role: str = "assistant"
    model: str = ""
    usage: Optional[Dict[str, int]] = None  # tokens used
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ToolCall:
    """工具调用"""
    name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None


class LLMClientABC(ABC):
    """LLM 客户端抽象基类

    定义所有 LLM 客户端必须实现的通用接口。
    """

    def __init__(self, api_key: str, model: str, **kwargs):
        """初始化 LLM 客户端

        Args:
            api_key: API 密钥
            model: 模型名称
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """发送聊天请求

        Args:
            messages: 消息历史
            tools: 可用的工具列表（用于 function calling）
            **kwargs: 其他参数

        Returns:
            LLM 响应
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """发送流式聊天请求

        Args:
            messages: 消息历史
            tools: 可用的工具列表
            **kwargs: 其他参数

        Yields:
            响应内容片段
        """
        pass

    @abstractmethod
    def set_system_prompt(self, prompt: str) -> None:
        """设置系统提示词

        Args:
            prompt: 系统提示词
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息

        Returns:
            模型信息字典
        """
        pass

    def create_message(self, role: str, content: str, **metadata) -> Message:
        """创建消息对象

        Args:
            role: 角色（system, user, assistant）
            content: 消息内容
            **metadata: 元数据

        Returns:
            消息对象
        """
        return Message(role=role, content=content, metadata=metadata or None)

    def format_messages(self, messages: List[Message]) -> List[Dict[str, str]]:
        """格式化消息列表

        Args:
            messages: 消息列表

        Returns:
            格式化后的消息列表
        """
        return [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
