"""
MCP Server Factory

工厂模式创建 MCP 服务器实例。
"""
from typing import Optional
from .base import MCPServerBase
from .gitlab_server import GitLabMCPServer
from .github_server import GitHubMCPServer
from core.enums import PlatformType
from infrastructure.database.models import UserConfigInDB
from utils.logger import get_logger


logger = get_logger(__name__)


class MCPServerFactory:
    """MCP 服务器工厂

    根据用户配置创建对应的 MCP 服务器实例。
    """

    @staticmethod
    def create_server(config: UserConfigInDB, platform: Optional[PlatformType] = None) -> MCPServerBase:
        """创建 MCP 服务器实例

        Args:
            config: 用户配置对象
            platform: 指定平台，如果为 None 则使用配置中的默认平台

        Returns:
            MCP 服务器实例

        Raises:
            ValueError: 如果平台不支持或配置不完整
        """
        # 确定使用的平台
        if platform is None:
            platform = PlatformType(config.default_platform)

        # 根据平台创建对应的服务器
        if platform == PlatformType.GITLAB:
            return MCPServerFactory._create_gitlab_server(config)
        elif platform == PlatformType.GITHUB:
            return MCPServerFactory._create_github_server(config)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    @staticmethod
    def _create_gitlab_server(config: UserConfigInDB) -> GitLabMCPServer:
        """创建 GitLab 服务器"""
        if not config.gitlab_url or not config.gitlab_token:
            raise ValueError("GitLab configuration is incomplete. Please provide gitlab_url and gitlab_token.")

        logger.info(f"Creating GitLab MCP server for user {config.user_id}")
        return GitLabMCPServer(config)

    @staticmethod
    def _create_github_server(config: UserConfigInDB) -> GitHubMCPServer:
        """创建 GitHub 服务器"""
        if not config.github_username or not config.github_token:
            raise ValueError("GitHub configuration is incomplete. Please provide github_username and github_token.")

        logger.info(f"Creating GitHub MCP server for user {config.user_id}")
        return GitHubMCPServer(config)

    @staticmethod
    def create_all_servers(config: UserConfigInDB) -> dict[PlatformType, MCPServerBase]:
        """创建所有已配置的服务器

        为用户配置的所有平台创建服务器实例。

        Args:
            config: 用户配置对象

        Returns:
            平台到服务器实例的字典
        """
        servers = {}

        # 尝试创建 GitLab 服务器
        try:
            servers[PlatformType.GITLAB] = MCPServerFactory._create_gitlab_server(config)
        except ValueError as e:
            logger.warning(f"Cannot create GitLab server: {str(e)}")

        # 尝试创建 GitHub 服务器
        try:
            servers[PlatformType.GITHUB] = MCPServerFactory._create_github_server(config)
        except ValueError as e:
            logger.warning(f"Cannot create GitHub server: {str(e)}")

        if not servers:
            raise ValueError("No valid platform configuration found. Please configure at least one platform.")

        return servers

    @staticmethod
    def get_default_server(config: UserConfigInDB) -> MCPServerBase:
        """获取默认平台的 MCP 服务器

        Args:
            config: 用户配置对象

        Returns:
            默认平台的 MCP 服务器实例

        Raises:
            ValueError: 如果默认平台配置不完整
        """
        return MCPServerFactory.create_server(config)
