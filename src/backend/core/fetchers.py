"""
Git Platform Fetchers

实现从 GitLab 和 GitHub 获取数据的类。
"""
from typing import List, Optional
from datetime import datetime
from .base import CommitFetcherABC
from .models import GitCommit, GitProject
from ..utils.api import APIClient


class GitLabFetcher(CommitFetcherABC):
    """GitLab 提交记录获取器"""

    def __init__(
        self,
        url: str,
        token: str,
        timeout: float = 30.0
    ):
        """初始化 GitLab 获取器

        Args:
            url: GitLab 服务器地址（如 https://gitlab.com）
            token: GitLab 访问令牌（Personal Access Token）
            timeout: 请求超时时间
        """
        self.url = url.rstrip("/")
        self.token = token
        self.api = APIClient(
            base_url=f"{self.url}/api/v4",
            headers={"PRIVATE-TOKEN": token},
            timeout=timeout
        )

    async def get_projects(self) -> List[GitProject]:
        """获取用户可访问的项目列表"""
        try:
            response = await self.api.get("/projects", params={
                "membership": True,
                "per_page": 100,
                "order_by": "last_activity_at",
                "sort": "desc"
            })

            projects = []
            for item in response:
                projects.append(GitProject(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description"),
                    web_url=item["web_url"],
                    default_branch=item.get("default_branch", "main"),
                    created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                    last_activity_at=datetime.fromisoformat(item["last_activity_at"].replace("Z", "+00:00"))
                ))

            return projects
        except Exception as e:
            raise RuntimeError(f"Failed to fetch GitLab projects: {str(e)}")

    async def get_project(self, project_id: str) -> Optional[GitProject]:
        """获取单个项目"""
        try:
            item = await self.api.get(f"/projects/{project_id}")

            return GitProject(
                id=item["id"],
                name=item["name"],
                description=item.get("description"),
                web_url=item["web_url"],
                default_branch=item.get("default_branch", "main"),
                created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                last_activity_at=datetime.fromisoformat(item["last_activity_at"].replace("Z", "+00:00"))
            )
        except Exception:
            return None

    async def get_commits(
        self,
        since_date: Optional[datetime] = None,
        until_date: Optional[datetime] = None,
        branch: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[GitCommit]:
        """获取提交记录

        Args:
            since_date: 起始日期
            until_date: 结束日期
            branch: 分支名称
            project_id: 项目 ID，如果为 None 则获取所有项目的提交

        Returns:
            提交记录列表
        """
        try:
            # 如果没有指定项目，先获取所有项目
            if project_id:
                projects = [await self.get_project(project_id)]
            else:
                projects = await self.get_projects()

            all_commits = []

            for project in projects:
                if project is None:
                    continue

                params = {
                    "per_page": 100,
                    "order_by": "created_at",
                    "sort": "desc"
                }

                if since_date:
                    params["since"] = since_date.isoformat()
                if until_date:
                    params["until"] = until_date.isoformat()
                if branch:
                    params["ref_name"] = branch

                try:
                    response = await self.api.get(
                        f"/projects/{project.id}/repository/commits",
                        params=params
                    )

                    for item in response:
                        commit = GitCommit(
                            id=item["id"],
                            short_id=item["short_id"],
                            title=item["title"],
                            message=item["message"],
                            author_name=item["author_name"],
                            author_email=item["author_email"],
                            authored_date=datetime.fromisoformat(item["authored_date"].replace("Z", "+00:00")),
                            committed_date=datetime.fromisoformat(item["committed_date"].replace("Z", "+00:00")),
                            web_url=f"{project.web_url}/-/commit/{item['id']}",
                            project_id=project.id,
                            project_name=project.name,
                            branch=branch or project.default_branch
                        )
                        all_commits.append(commit)

                except Exception as e:
                    # 单个项目失败不影响其他项目
                    print(f"Warning: Failed to fetch commits from project {project.name}: {str(e)}")
                    continue

            # 按提交时间排序（最新的在前）
            all_commits.sort(key=lambda c: c.committed_date, reverse=True)

            return all_commits

        except Exception as e:
            raise RuntimeError(f"Failed to fetch GitLab commits: {str(e)}")


class GitHubFetcher(CommitFetcherABC):
    """GitHub 提交记录获取器"""

    def __init__(
        self,
        username: str,
        token: str,
        timeout: float = 30.0
    ):
        """初始化 GitHub 获取器

        Args:
            username: GitHub 用户名
            token: GitHub 访问令牌（Personal Access Token）
            timeout: 请求超时时间
        """
        self.username = username
        self.token = token
        self.api = APIClient(
            base_url="https://api.github.com",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            },
            timeout=timeout
        )

    async def get_projects(self) -> List[GitProject]:
        """获取用户的项目列表（仓库）"""
        try:
            response = await self.api.get(f"/users/{self.username}/repos", params={
                "type": "all",
                "sort": "updated",
                "per_page": 100
            })

            projects = []
            for item in response:
                projects.append(GitProject(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description"),
                    web_url=item["html_url"],
                    default_branch=item.get("default_branch", "main"),
                    created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                    last_activity_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
                ))

            return projects
        except Exception as e:
            raise RuntimeError(f"Failed to fetch GitHub repositories: {str(e)}")

    async def get_project(self, project_id: str) -> Optional[GitProject]:
        """获取单个项目（仓库）"""
        try:
            # GitHub 使用 owner/repo 格式
            item = await self.api.get(f"/repos/{project_id}")

            return GitProject(
                id=item["id"],
                name=item["name"],
                description=item.get("description"),
                web_url=item["html_url"],
                default_branch=item.get("default_branch", "main"),
                created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                last_activity_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
            )
        except Exception:
            return None

    async def get_commits(
        self,
        since_date: Optional[datetime] = None,
        until_date: Optional[datetime] = None,
        branch: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[GitCommit]:
        """获取提交记录"""
        try:
            # 如果没有指定项目，先获取所有项目
            if project_id:
                projects = [await self.get_project(project_id)]
            else:
                projects = await self.get_projects()

            all_commits = []

            for project in projects:
                if project is None:
                    continue

                params = {
                    "per_page": 100
                }

                if since_date:
                    params["since"] = since_date.isoformat()
                if until_date:
                    params["until"] = until_date.isoformat()
                if branch:
                    params["sha"] = branch

                try:
                    response = await self.api.get(
                        f"/repos/{self.username}/{project.name}/commits",
                        params=params
                    )

                    for item in response:
                        commit = GitCommit(
                            id=item["sha"],
                            short_id=item["sha"][:7],
                            title=item["commit"]["message"].split("\n")[0],
                            message=item["commit"]["message"],
                            author_name=item["commit"]["author"]["name"],
                            author_email=item["commit"]["author"]["email"],
                            authored_date=datetime.fromisoformat(item["commit"]["author"]["date"].replace("Z", "+00:00")),
                            committed_date=datetime.fromisoformat(item["commit"]["committer"]["date"].replace("Z", "+00:00")),
                            web_url=item["html_url"],
                            project_id=project.id,
                            project_name=project.name,
                            branch=branch or project.default_branch
                        )
                        all_commits.append(commit)

                except Exception as e:
                    print(f"Warning: Failed to fetch commits from repository {project.name}: {str(e)}")
                    continue

            all_commits.sort(key=lambda c: c.committed_date, reverse=True)

            return all_commits

        except Exception as e:
            raise RuntimeError(f"Failed to fetch GitHub commits: {str(e)}")
