"""
GitHub MCP Server

实现 GitHub 平台的 MCP 服务器。
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .base import MCPServerBase
from ..core.fetchers import GitHubFetcher
from ..core.models import GitCommit, GitProject
from ..utils.logger import get_logger


logger = get_logger(__name__)


class GitHubMCPServer(MCPServerBase):
    """GitHub MCP 服务器

    提供与 GitHub 交互的工具，包括：
    - 获取提交记录
    - 获取仓库列表
    - 搜索提交
    - 获取仓库详情
    """

    def __init__(self, config: Any):
        """初始化 GitHub MCP 服务器

        Args:
            config: 用户配置对象，必须包含 github_username 和 github_token
        """
        super().__init__(config)

        # 验证配置
        if not hasattr(config, 'github_username') or not config.github_username:
            raise ValueError("github_username is required in config")

        if not hasattr(config, 'github_token') or not config.github_token:
            raise ValueError("github_token is required in config")

        # 初始化 GitHub 获取器
        self.fetcher = GitHubFetcher(
            username=config.github_username,
            token=config.github_token
        )

        logger.info(f"GitHub MCP Server initialized for user {self.user_id}")

    async def get_tools(self) -> List[Dict[str, Any]]:
        """获取可用的工具列表"""
        return [
            {
                "name": "get_github_commits",
                "description": "Get Git commit history from GitHub repositories",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "since_date": {
                            "type": "string",
                            "description": "Start date in ISO format (e.g., 2026-01-01T00:00:00)"
                        },
                        "until_date": {
                            "type": "string",
                            "description": "End date in ISO format (e.g., 2026-01-31T23:59:59)"
                        },
                        "branch": {
                            "type": "string",
                            "description": "Branch name (e.g., main, master)"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Specific repository name (e.g., username/repo-name)"
                        }
                    }
                }
            },
            {
                "name": "get_github_repositories",
                "description": "Get list of GitHub repositories for the user",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_github_repository",
                "description": "Get details of a specific GitHub repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository name (e.g., username/repo-name)"
                        }
                    },
                    "required": ["repo"]
                }
            },
            {
                "name": "search_github_commits",
                "description": "Search GitHub commits by message content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for commit messages"
                        },
                        "since_date": {
                            "type": "string",
                            "description": "Start date in ISO format"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """调用工具"""
        try:
            if name == "get_github_commits":
                return await self._get_commits_tool(arguments)
            elif name == "get_github_repositories":
                return await self._get_repositories_tool()
            elif name == "get_github_repository":
                return await self._get_repository_tool(arguments)
            elif name == "search_github_commits":
                return await self._search_commits_tool(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Error calling tool {name}: {str(e)}")
            raise

    async def get_commits(
        self,
        since_date: Optional[datetime] = None,
        until_date: Optional[datetime] = None,
        branch: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[GitCommit]:
        """获取提交记录

        Note: GitHub 使用 'repo' 参数代替 'project_id'
        """
        self.validate_date_range(since_date, until_date)

        logger.info(f"Fetching GitHub commits for user {self.user_id}")
        commits = await self.fetcher.get_commits(since_date, until_date, branch, project_id)

        logger.info(f"Retrieved {len(commits)} commits from GitHub")
        return commits

    async def get_projects(self) -> List[GitProject]:
        """获取项目列表（仓库）"""
        logger.info(f"Fetching GitHub repositories for user {self.user_id}")
        projects = await self.fetcher.get_projects()

        logger.info(f"Retrieved {len(projects)} repositories from GitHub")
        return projects

    # 工具实现方法

    async def _get_commits_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """获取提交记录工具实现"""
        since_date = None
        until_date = None

        if "since_date" in arguments:
            since_date = datetime.fromisoformat(arguments["since_date"])

        if "until_date" in arguments:
            until_date = datetime.fromisoformat(arguments["until_date"])

        branch = arguments.get("branch")
        repo = arguments.get("repo")  # GitHub 使用 repo 而非 project_id

        commits = await self.get_commits(since_date, until_date, branch, repo)

        return {
            "count": len(commits),
            "commits": [
                {
                    "id": c.id,
                    "short_id": c.short_id,
                    "title": c.title,
                    "message": c.message,
                    "author_name": c.author_name,
                    "authored_date": c.authored_date.isoformat(),
                    "web_url": c.web_url,
                    "project_name": c.project_name,
                    "branch": c.branch
                }
                for c in commits
            ]
        }

    async def _get_repositories_tool(self) -> Dict[str, Any]:
        """获取仓库列表工具实现"""
        projects = await self.get_projects()

        return {
            "count": len(projects),
            "repositories": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "web_url": p.web_url,
                    "default_branch": p.default_branch,
                    "last_activity_at": p.last_activity_at.isoformat()
                }
                for p in projects
            ]
        }

    async def _get_repository_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """获取单个仓库工具实现"""
        repo = arguments.get("repo")

        if not repo:
            raise ValueError("repo is required")

        project = await self.fetcher.get_project(repo)

        if not project:
            return {"error": f"Repository {repo} not found"}

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "web_url": project.web_url,
            "default_branch": project.default_branch,
            "created_at": project.created_at.isoformat(),
            "last_activity_at": project.last_activity_at.isoformat()
        }

    async def _search_commits_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """搜索提交记录工具实现"""
        query = arguments.get("query", "").lower()

        if not query:
            raise ValueError("query is required")

        since_date = None
        if "since_date" in arguments:
            since_date = datetime.fromisoformat(arguments["since_date"])

        # 获取所有提交（带日期过滤）
        commits = await self.get_commits(since_date=since_date)

        # 过滤匹配的提交
        matching_commits = [
            c for c in commits
            if query in c.title.lower() or query in c.message.lower()
        ]

        logger.info(f"Found {len(matching_commits)} commits matching '{query}'")

        return {
            "query": query,
            "count": len(matching_commits),
            "commits": [
                {
                    "id": c.id,
                    "short_id": c.short_id,
                    "title": c.title,
                    "message": c.message,
                    "author_name": c.author_name,
                    "authored_date": c.authored_date.isoformat(),
                    "web_url": c.web_url,
                    "project_name": c.project_name
                }
                for c in matching_commits
            ]
        }

    async def get_this_week_commits(self) -> List[GitCommit]:
        """获取本周的提交记录（便捷方法）"""
        today = datetime.now()
        since_date = today - timedelta(days=today.weekday())
        since_date = since_date.replace(hour=0, minute=0, second=0, microsecond=0)

        return await self.get_commits(since_date=since_date)

    async def get_this_month_commits(self) -> List[GitCommit]:
        """获取本月的提交记录（便捷方法）"""
        today = datetime.now()
        since_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        return await self.get_commits(since_date=since_date)
