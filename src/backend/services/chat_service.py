"""
Chat Service

聊天服务，协调 LLM 和 MCP 工具调用。
"""
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from llm import Message, LLMResponse, get_llm_client, get_worklog_assistant_prompt
from mcp_servers import MCPServerFactory
from infrastructure.database.models import UserConfigInDB
from utils.logger import get_logger
from utils.datetime import (
    get_today_range,
    get_week_range,
    get_month_range,
    get_date_range
)


logger = get_logger(__name__)


class ToolExecutor:
    """工具执行器

    执行 MCP 工具调用。
    """

    def __init__(self, config: UserConfigInDB):
        """初始化工具执行器

        Args:
            config: 用户配置对象
        """
        self.config = config
        self.servers = MCPServerFactory.create_all_servers(config)
        self.default_server = MCPServerFactory.get_default_server(config)

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """执行工具

        Args:
            name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果

        Raises:
            ValueError: 如果工具不存在或执行失败
        """
        try:
            # 解析时间参数
            processed_args = self._process_arguments(arguments)

            # 确定使用哪个服务器
            if name.startswith("gitlab_"):
                server = self.servers.get("gitlab")
                tool_name = name.replace("gitlab_", "")
            elif name.startswith("github_"):
                server = self.servers.get("github")
                tool_name = name.replace("github_", "")
            else:
                # 使用默认服务器
                server = self.default_server
                tool_name = name

            if not server:
                raise ValueError(f"No server configured for tool: {name}")

            # 调用工具
            result = await server.call_tool(tool_name, processed_args)
            return result

        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}")
            raise

    def _process_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理参数，解析时间范围等

        Args:
            arguments: 原始参数

        Returns:
            处理后的参数
        """
        processed = {}

        for key, value in arguments.items():
            if key.endswith("_date") and isinstance(value, str):
                # 解析日期字符串
                try:
                    processed[key] = datetime.fromisoformat(value)
                except:
                    processed[key] = value
            else:
                processed[key] = value

        return processed

    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取所有可用的工具

        Returns:
            工具列表
        """
        all_tools = []

        for platform, server in self.servers.items():
            tools = await server.get_tools()
            all_tools.extend(tools)

        return all_tools


class ChatService:
    """聊天服务

    处理用户消息，协调 LLM 和工具调用。
    """

    def __init__(self):
        """初始化聊天服务"""
        self.llm_client = get_llm_client()
        self.llm_client.set_system_prompt(get_worklog_assistant_prompt())

    async def chat(
        self,
        user_message: str,
        user_id: int,
        config: UserConfigInDB,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """处理聊天消息

        Args:
            user_message: 用户消息
            user_id: 用户 ID
            config: 用户配置
            chat_history: 聊天历史（可选）

        Returns:
            包含回复和元数据的字典
        """
        start_time = time.time()

        try:
            # 创建工具执行器
            tool_executor = ToolExecutor(config)

            # 获取可用工具
            tools = await tool_executor.get_available_tools()

            # 准备消息历史
            messages = self._prepare_messages(user_message, chat_history)

            # 调用 LLM（带工具执行）
            response = await self.llm_client.chat_with_tools(
                messages=messages,
                tools=tools,
                tool_executor=tool_executor,
                max_iterations=5
            )

            # 计算处理时间
            processing_time = time.time() - start_time

            # 准备返回数据
            return {
                "content": response.content,
                "role": "assistant",
                "metadata": {
                    "model": response.model,
                    "usage": response.usage,
                    "processing_time": processing_time,
                    "tool_calls": response.metadata.get("tool_calls") if response.metadata else None
                }
            }

        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            return {
                "content": f"抱歉，处理您的请求时出现错误：{str(e)}",
                "role": "assistant",
                "metadata": {
                    "error": str(e),
                    "processing_time": time.time() - start_time
                }
            }

    def _prepare_messages(
        self,
        user_message: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Message]:
        """准备消息列表

        Args:
            user_message: 当前用户消息
            chat_history: 聊天历史

        Returns:
            消息列表
        """
        messages = []

        # 添加聊天历史
        if chat_history:
            for msg in chat_history[-10:]:  # 只保留最近10条
                if msg["role"] in ["user", "assistant"]:
                    messages.append(Message(
                        role=msg["role"],
                        content=msg["content"]
                    ))

        # 添加当前消息
        messages.append(Message(role="user", content=user_message))

        return messages

    async def parse_time_request(self, message: str) -> Dict[str, Any]:
        """解析时间请求

        从用户消息中提取时间范围。

        Args:
            message: 用户消息

        Returns:
            包含 since_date 和 until_date 的字典
        """
        message_lower = message.lower()

        # 今天
        if "今天" in message:
            start, end = get_today_range()
            return {"since_date": start, "until_date": end}

        # 本周
        if "本周" in message or "这周" in message:
            start, end = get_week_range()
            return {"since_date": start, "until_date": end}

        # 上周
        if "上周" in message:
            today = datetime.now()
            last_week_start = today - timedelta(days=today.weekday() + 7)
            last_week_start = last_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            last_week_end = last_week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
            return {"since_date": last_week_start, "until_date": last_week_end}

        # 本月
        if "本月" in message or "这个月" in message:
            start, end = get_month_range()
            return {"since_date": start, "until_date": end}

        # 上月
        if "上月" in message or "上个月" in message:
            today = datetime.now()
            if today.month == 1:
                last_month = today.replace(year=today.year - 1, month=12, day=1)
            else:
                last_month = today.replace(month=today.month - 1, day=1)

            start = last_month.replace(hour=0, minute=0, second=0, microsecond=0)
            # 月末
            if last_month.month == 12:
                next_month = last_month.replace(year=last_month.year + 1, month=1, day=1)
            else:
                next_month = last_month.replace(month=last_month.month + 1, day=1)
            end = next_month - timedelta(seconds=1)

            return {"since_date": start, "until_date": end}

        # 最近N天
        import re
        match = re.search(r'最近(\d+)天', message)
        if match:
            days = int(match.group(1))
            start, end = get_date_range(days)
            return {"since_date": start, "until_date": end}

        # 默认：本周
        start, end = get_week_range()
        return {"since_date": start, "until_date": end}


# 全局单例
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """获取聊天服务实例"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
