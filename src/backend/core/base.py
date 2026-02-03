"""
Core Base Classes

定义系统核心抽象基类。
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import GitCommit, GitProject, WorkLogReport


class CommitFetcherABC(ABC):
    """提交记录获取器抽象基类

    定义从 Git 平台获取提交记录的通用接口。
    """

    @abstractmethod
    def get_commits(
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
            project_id: 项目 ID

        Returns:
            提交记录列表
        """
        pass

    @abstractmethod
    def get_projects(self) -> List[GitProject]:
        """获取项目列表

        Returns:
            项目列表
        """
        pass

    @abstractmethod
    def get_project(self, project_id: str) -> Optional[GitProject]:
        """获取单个项目

        Args:
            project_id: 项目 ID

        Returns:
            项目信息，如果不存在则返回 None
        """
        pass


class WorkLogGeneratorABC(ABC):
    """工作日志生成器抽象基类

    定义生成工作日志的通用接口。
    """

    @abstractmethod
    def generate(self, commits: List[GitCommit]) -> WorkLogReport:
        """根据提交记录生成工作日志报告

        Args:
            commits: 提交记录列表

        Returns:
            工作日志报告
        """
        pass

    @abstractmethod
    def format_markdown(self, report: WorkLogReport) -> str:
        """将工作日志报告格式化为 Markdown

        Args:
            report: 工作日志报告

        Returns:
            Markdown 格式的字符串
        """
        pass


class CommitAnalyzerABC(ABC):
    """提交记录分析器抽象基类

    定义分析提交记录的通用接口。
    """

    @abstractmethod
    def analyze(self, commits: List[GitCommit]) -> Dict[str, Any]:
        """分析提交记录

        Args:
            commits: 提交记录列表

        Returns:
            分析结果字典，包含统计信息、任务分类等
        """
        pass

    @abstractmethod
    def classify_task(self, commit: GitCommit) -> str:
        """根据提交信息分类任务类型

        Args:
            commit: 提交记录

        Returns:
            任务类型
        """
        pass
