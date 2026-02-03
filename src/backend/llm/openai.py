"""
OpenAI LLM Client Implementation

使用 OpenAI API 的客户端实现。
"""
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from openai import AsyncOpenAI
import json

from .base import LLMClientABC, Message, LLMResponse, ToolCall
from ..utils.logger import get_logger


logger = get_logger(__name__)


class OpenAIClient(LLMClientABC):
    """OpenAI LLM 客户端

    使用 OpenAI 的模型（GPT-4, GPT-3.5等）进行对话和工具调用。
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """初始化 OpenAI 客户端

        Args:
            api_key: OpenAI API 密钥
            model: 模型名称（如 gpt-4, gpt-3.5-turbo）
            temperature: 温度参数（0-1）
            max_tokens: 最大生成 token 数
            base_url: API 基础 URL（用于兼容 API）
            **kwargs: 其他配置参数
        """
        super().__init__(api_key, model, **kwargs)

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = AsyncOpenAI(**client_kwargs)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt: Optional[str] = None

        logger.info(f"OpenAI client initialized with model: {model}")

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
                "temperature": kwargs.get("temperature", self.temperature),
                "messages": self._format_messages(messages)
            }

            # 设置 max_tokens（如果支持）
            if self.model.startswith("gpt-"):
                api_params["max_tokens"] = kwargs.get("max_tokens", self.max_tokens)

            # 添加工具（如果提供）
            if tools:
                api_params["tools"] = self._format_tools(tools)
                api_params["tool_choice"] = "auto"

            # 调用 API
            response = await self.client.chat.completions.create(**api_params)

            # 解析响应
            return self._parse_response(response)

        except Exception as e:
            logger.error(f"Error in OpenAI chat: {str(e)}")
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
                "temperature": kwargs.get("temperature", self.temperature),
                "messages": self._format_messages(messages),
                "stream": True
            }

            if self.model.startswith("gpt-"):
                api_params["max_tokens"] = kwargs.get("max_tokens", self.max_tokens)

            # 流式调用
            stream = await self.client.chat.completions.create(**api_params)

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in OpenAI stream: {str(e)}")
            raise

    def set_system_prompt(self, prompt: str) -> None:
        """设置系统提示词"""
        self.system_prompt = prompt

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "openai",
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

    def _format_messages(self, messages: List[Message]) -> List[Dict[str, str]]:
        """格式化消息列表为 OpenAI API 格式"""
        formatted = []

        # 添加系统提示词
        if self.system_prompt:
            formatted.append({"role": "system", "content": self.system_prompt})

        # 添加消息
        for msg in messages:
            if msg.role == "system" and self.system_prompt:
                # 如果有单独的 system_prompt，跳过消息中的 system
                continue
            formatted.append({
                "role": msg.role,
                "content": msg.content
            })

        return formatted

    def _format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化工具列表为 OpenAI API 格式

        OpenAI 的工具格式：
        {
            "type": "function",
            "function": {
                "name": "tool_name",
                "description": "Tool description",
                "parameters": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }
        }
        """
        formatted_tools = []
        for tool in tools:
            formatted_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", tool.get("input_schema", {}))
                }
            }
            formatted_tools.append(formatted_tool)
        return formatted_tools

    def _parse_response(self, response) -> LLMResponse:
        """解析 OpenAI API 响应

        Args:
            response: OpenAI completion 对象

        Returns:
            LLMResponse 对象
        """
        # 提取内容
        message = response.choices[0].message
        content = message.content or ""

        # 提取工具调用
        tool_calls = []
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append(ToolCall(
                    name=tool_call.function.name,
                    arguments=json.loads(tool_call.function.arguments)
                ))

        # 提取使用量
        usage = None
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

        return LLMResponse(
            content=content,
            role="assistant",
            model=response.model,
            usage=usage,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
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

                    # OpenAI 需要特定的工具消息格式
                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": f"call_{iteration}_{tool_call.name}",
                        "content": json.dumps(result, ensure_ascii=False)
                    })

                except Exception as e:
                    tool_call.error = str(e)
                    logger.error(f"Error executing tool {tool_call.name}: {str(e)}")

                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": f"call_{iteration}_{tool_call.name}",
                        "content": json.dumps({"error": str(e)}, ensure_ascii=False)
                    })

        # 达到最大迭代次数
        return await self.chat(current_messages, **kwargs)
