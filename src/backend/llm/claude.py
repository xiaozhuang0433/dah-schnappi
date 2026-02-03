"""
Claude LLM Client Implementation

使用 Anthropic API 的 Claude 客户端实现。
"""
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from anthropic import AsyncAnthropic
from anthropic.types import Message as AnthropicMessage
import json

from .base import LLMClientABC, Message, LLMResponse, ToolCall
from ..utils.logger import get_logger


logger = get_logger(__name__)


class ClaudeClient(LLMClientABC):
    """Claude LLM 客户端

    使用 Anthropic 的 Claude 模型进行对话和工具调用。
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ):
        """初始化 Claude 客户端

        Args:
            api_key: Anthropic API 密钥
            model: 模型名称
            temperature: 温度参数（0-1）
            max_tokens: 最大生成 token 数
            **kwargs: 其他配置参数
        """
        super().__init__(api_key, model, **kwargs)

        self.client = AsyncAnthropic(api_key=api_key)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt: Optional[str] = None

        logger.info(f"Claude client initialized with model: {model}")

    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """发送聊天请求

        Args:
            messages: 消息历史
            tools: 可用的工具列表
            **kwargs: 其他参数

        Returns:
            LLM 响应
        """
        try:
            # 准备参数
            api_params = {
                "model": self.model,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "messages": self._format_messages(messages)
            }

            # 添加系统提示词
            if self.system_prompt:
                api_params["system"] = self.system_prompt

            # 添加工具（如果提供）
            if tools:
                api_params["tools"] = self._format_tools(tools)

            # 调用 API
            response = await self.client.messages.create(**api_params)

            # 解析响应
            return self._parse_response(response)

        except Exception as e:
            logger.error(f"Error in Claude chat: {str(e)}")
            raise

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
        try:
            # 准备参数
            api_params = {
                "model": self.model,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "messages": self._format_messages(messages)
            }

            if self.system_prompt:
                api_params["system"] = self.system_prompt

            if tools:
                api_params["tools"] = self._format_tools(tools)

            # 流式调用
            async with self.client.messages.stream(**api_params) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Error in Claude stream: {str(e)}")
            raise

    def set_system_prompt(self, prompt: str) -> None:
        """设置系统提示词"""
        self.system_prompt = prompt

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "anthropic",
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

    def _format_messages(self, messages: List[Message]) -> List[Dict[str, str]]:
        """格式化消息列表为 Claude API 格式"""
        formatted = []
        for msg in messages:
            # Claude 不接受 system 角色在 messages 中，需要单独处理
            if msg.role == "system":
                continue
            formatted.append({
                "role": msg.role,
                "content": msg.content
            })
        return formatted

    def _format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化工具列表为 Claude API 格式

        Claude 的工具格式：
        {
            "name": "tool_name",
            "description": "Tool description",
            "input_schema": {
                "type": "object",
                "properties": {...},
                "required": [...]
            }
        }
        """
        formatted_tools = []
        for tool in tools:
            formatted_tool = {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "input_schema": tool.get("inputSchema", tool.get("input_schema", {}))
            }
            formatted_tools.append(formatted_tool)
        return formatted_tools

    def _parse_response(self, response: AnthropicMessage) -> LLMResponse:
        """解析 Claude API 响应

        Args:
            response: Anthropic Message 对象

        Returns:
            LLMResponse 对象
        """
        # 提取文本内容
        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        # 提取工具调用
        tool_calls = []
        for block in response.content:
            if block.type == "tool_use":
                tool_calls.append(ToolCall(
                    name=block.name,
                    arguments=block.input
                ))

        return LLMResponse(
            content=content,
            role="assistant",
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            metadata={
                "stop_reason": response.stop_reason,
                "tool_calls": [tc.__dict__ for tc in tool_calls] if tool_calls else None
            }
        )

    async def chat_with_tools(
        self,
        messages: List[Message],
        tools: List[Dict[str, Any]],
        tool_executor: Any,
        max_iterations: int = 5,
        **kwargs
    ) -> LLMResponse:
        """带工具执行的聊天

        自动处理工具调用循环。

        Args:
            messages: 消息历史
            tools: 可用的工具列表
            tool_executor: 工具执行器（需要实现 execute_tool 方法）
            max_iterations: 最大迭代次数
            **kwargs: 其他参数

        Returns:
            最终的 LLM 响应
        """
        current_messages = messages.copy()
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # 调用 LLM
            response = await self.chat(current_messages, tools=tools, **kwargs)

            # 检查是否有工具调用
            tool_calls = response.metadata.get("tool_calls")
            if not tool_calls:
                # 没有工具调用，返回最终响应
                return response

            # 执行工具调用
            current_messages.append(Message(role="assistant", content=response.content))

            for tool_call_dict in tool_calls:
                tool_call = ToolCall(**tool_call_dict)

                # 执行工具
                try:
                    result = await tool_executor.execute_tool(
                        tool_call.name,
                        tool_call.arguments
                    )
                    tool_call.result = result

                    # 添加工具结果到消息历史
                    current_messages.append(Message(
                        role="user",
                        content=json.dumps({
                            "tool_name": tool_call.name,
                            "result": result
                        }, ensure_ascii=False)
                    ))

                except Exception as e:
                    tool_call.error = str(e)
                    logger.error(f"Error executing tool {tool_call.name}: {str(e)}")

                    # 添加错误信息
                    current_messages.append(Message(
                        role="user",
                        content=json.dumps({
                            "tool_name": tool_call.name,
                            "error": str(e)
                        }, ensure_ascii=False)
                    ))

        # 达到最大迭代次数
        return await self.chat(current_messages, **kwargs)
