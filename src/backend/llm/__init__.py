"""
LLM Package

导出 LLM 相关模块。
"""
from .base import LLMClientABC, Message, LLMResponse, ToolCall
from .claude import ClaudeClient
from .openai import OpenAIClient
from .client import LLMClientFactory, get_llm_client
from .prompts import (
    get_worklog_assistant_prompt,
    get_quick_assistant_prompt,
    get_chinese_assistant_prompt
)

__all__ = [
    # Base
    "LLMClientABC",
    "Message",
    "LLMResponse",
    "ToolCall",
    # Implementations
    "ClaudeClient",
    "OpenAIClient",
    # Factory
    "LLMClientFactory",
    "get_llm_client",
    # Prompts
    "get_worklog_assistant_prompt",
    "get_quick_assistant_prompt",
    "get_chinese_assistant_prompt"
]
