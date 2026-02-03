"""
MCP Server Base Class

定义 MCP 服务器的抽象基类。
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class MCPServerBase(ABC):
    """MCP 服务器抽象基类

    定义所有 MCP 服务器必须实现的通用接口。
    """

    def __init__(self, config: Any):
        """初始化 MCP 服务器

        Args:
            config: 配置对象（通常是 UserConfigInDB）
        """
        self.config = config
        self.user_id = config.user_id if hasattr(config, 'user_id') else None

    @abstractmethod
    async def get_tools(self) -> List[Dict[str, Any]]:
        """获取可用的工具列表

        Returns:
            工具定义列表，每个工具包含:
            - name: 工具名称
            - description: 工具描述
            - input_schema: 输入参数的 JSON Schema
        """
        pass

    @abstractmethod
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """调用工具

        Args:
            name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果

        Raises:
            ValueError: 如果工具不存在
            Exception: 如果工具执行失败
        """
        pass

    @abstractmethod
    async def get_commits(
        self,
        since_date: Optional[datetime] = None,
        until_date: Optional[datetime] = None,
        branch: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[Any]:
        """获取提交记录

        Args:
            since_date: 起始日期
            until_date: 结束日期
            branch: 分支名称
            project_id: 项目 ID

        Returns:
            提交记录列表
        """
        pass

    @abstractmethod
    async def get_projects(self) -> List[Any]:
        """获取项目列表

        Returns:
            项目列表
        """
        pass

    def validate_date_range(
        self,
        since_date: Optional[datetime],
        until_date: Optional[datetime]
    ) -> None:
        """验证日期范围

        Args:
            since_date: 起始日期
            until_date: 结束日期

        Raises:
            ValueError: 如果日期范围无效
        """
        if since_date and until_date and since_date > until_date:
            raise ValueError("since_date must be before or equal to until_date")

    def format_date(
        self,
        date: Optional[datetime],
        default: Optional[datetime] = None
    ) -> Optional[str]:
        """格式化日期

        Args:
            date: 日期对象
            default: 默认值

        Returns:
            ISO 格式日期字符串
        """
        if date is None:
            return default
        return date.isoformat()

    async def health_check(self) -> Dict[str, Any]:
        """健康检查

        Returns:
            健康状态信息
        """
        return {
            "status": "healthy",
            "server": self.__class__.__name__,
            "user_id": self.user_id
        }
