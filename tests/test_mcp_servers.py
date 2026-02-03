"""
MCP Servers Tests

测试 MCP 服务器功能。
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from src.mcp_servers import MCPServerFactory, GitLabMCPServer, GitHubMCPServer
from src.infrastructure.database.models import UserConfigInDB, PlatformType


@pytest.fixture
def mock_gitlab_config():
    """模拟 GitLab 配置"""
    config = Mock(spec=UserConfigInDB)
    config.user_id = 1
    config.gitlab_url = "https://gitlab.example.com"
    config.gitlab_token = "glpat-testtoken123"
    config.github_username = None
    config.github_token = None
    config.default_platform = PlatformType.GITLAB
    return config


@pytest.fixture
def mock_github_config():
    """模拟 GitHub 配置"""
    config = Mock(spec=UserConfigInDB)
    config.user_id = 2
    config.gitlab_url = None
    config.gitlab_token = None
    config.github_username = "testuser"
    config.github_token = "ghp_testtoken123"
    config.default_platform = PlatformType.GITHUB
    return config


class TestMCPServerFactory:
    """测试 MCP 服务器工厂"""

    def test_create_gitlab_server(self, mock_gitlab_config):
        """测试创建 GitLab 服务器"""
        server = MCPServerFactory.create_server(mock_gitlab_config, PlatformType.GITLAB)

        assert isinstance(server, GitLabMCPServer)
        assert server.user_id == 1

    def test_create_github_server(self, mock_github_config):
        """测试创建 GitHub 服务器"""
        server = MCPServerFactory.create_server(mock_github_config, PlatformType.GITHUB)

        assert isinstance(server, GitHubMCPServer)
        assert server.user_id == 2

    def test_create_server_with_incomplete_config(self, mock_gitlab_config):
        """测试配置不完整时创建服务器"""
        mock_gitlab_config.gitlab_url = None

        with pytest.raises(ValueError, match="GitLab configuration is incomplete"):
            MCPServerFactory.create_server(mock_gitlab_config, PlatformType.GITLAB)

    def test_get_default_server(self, mock_gitlab_config):
        """测试获取默认服务器"""
        server = MCPServerFactory.get_default_server(mock_gitlab_config)

        assert isinstance(server, GitLabMCPServer)


class TestGitLabMCPServer:
    """测试 GitLab MCP 服务器"""

    def test_initialization(self, mock_gitlab_config):
        """测试初始化"""
        server = GitLabMCPServer(mock_gitlab_config)

        assert server.user_id == 1
        assert server.config == mock_gitlab_config

    def test_initialization_with_missing_config(self):
        """测试配置缺失时初始化失败"""
        config = Mock(spec=UserConfigInDB)
        config.user_id = 1
        config.gitlab_url = None
        config.gitlab_token = "glpat-testtoken123"

        with pytest.raises(ValueError, match="gitlab_url is required"):
            GitLabMCPServer(config)

    @pytest.mark.asyncio
    async def test_get_tools(self, mock_gitlab_config):
        """测试获取工具列表"""
        server = GitLabMCPServer(mock_gitlab_config)
        tools = await server.get_tools()

        assert len(tools) == 4
        tool_names = [t["name"] for t in tools]
        assert "get_gitlab_commits" in tool_names
        assert "get_gitlab_projects" in tool_names
        assert "get_gitlab_project" in tool_names
        assert "search_gitlab_commits" in tool_names

    @pytest.mark.asyncio
    async def test_health_check(self, mock_gitlab_config):
        """测试健康检查"""
        server = GitLabMCPServer(mock_gitlab_config)
        health = await server.health_check()

        assert health["status"] == "healthy"
        assert health["server"] == "GitLabMCPServer"
        assert health["user_id"] == 1

    def test_validate_date_range_valid(self, mock_gitlab_config):
        """测试有效的日期范围验证"""
        server = GitLabMCPServer(mock_gitlab_config)

        # 不应该抛出异常
        server.validate_date_range(
            datetime(2026, 1, 1),
            datetime(2026, 1, 31)
        )

    def test_validate_date_range_invalid(self, mock_gitlab_config):
        """测试无效的日期范围验证"""
        server = GitLabMCPServer(mock_gitlab_config)

        with pytest.raises(ValueError, match="since_date must be before"):
            server.validate_date_range(
                datetime(2026, 1, 31),
                datetime(2026, 1, 1)
            )


class TestGitHubMCPServer:
    """测试 GitHub MCP 服务器"""

    def test_initialization(self, mock_github_config):
        """测试初始化"""
        server = GitHubMCPServer(mock_github_config)

        assert server.user_id == 2
        assert server.config == mock_github_config

    def test_initialization_with_missing_config(self):
        """测试配置缺失时初始化失败"""
        config = Mock(spec=UserConfigInDB)
        config.user_id = 2
        config.github_username = "testuser"
        config.github_token = None

        with pytest.raises(ValueError, match="github_token is required"):
            GitHubMCPServer(config)

    @pytest.mark.asyncio
    async def test_get_tools(self, mock_github_config):
        """测试获取工具列表"""
        server = GitHubMCPServer(mock_github_config)
        tools = await server.get_tools()

        assert len(tools) == 4
        tool_names = [t["name"] for t in tools]
        assert "get_github_commits" in tool_names
        assert "get_github_repositories" in tool_names
        assert "get_github_repository" in tool_names
        assert "search_github_commits" in tool_names

    @pytest.mark.asyncio
    async def test_health_check(self, mock_github_config):
        """测试健康检查"""
        server = GitHubMCPServer(mock_github_config)
        health = await server.health_check()

        assert health["status"] == "healthy"
        assert health["server"] == "GitHubMCPServer"
        assert health["user_id"] == 2
