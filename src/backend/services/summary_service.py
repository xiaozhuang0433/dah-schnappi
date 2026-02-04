"""
Summary Service

工作日志生成服务，从提交记录生成 Markdown 工作日志。
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from core.models import GitCommit, WorkLogEntry, WorkLogReport
from core.enums import TaskType
from utils.logger import get_logger


logger = get_logger(__name__)


class SummaryService:
    """工作日志生成服务

    将 Git 提交记录转换为格式化的 Markdown 工作日志。
    """

    def __init__(self):
        """初始化服务"""
        pass

    def generate_worklog_report(
        self,
        commits: List[GitCommit],
        start_date: datetime,
        end_date: datetime
    ) -> WorkLogReport:
        """生成工作日志报告

        Args:
            commits: 提交记录列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            工作日志报告
        """
        # 按日期分组提交
        entries_by_date = self._group_commits_by_date(commits)

        # 生成日志条目
        entries = []
        for date, date_commits in entries_by_date.items():
            entry = self._create_log_entry(date, date_commits)
            entries.append(entry)

        # 统计项目
        projects = self._get_unique_projects(commits)

        # 生成报告
        report = WorkLogReport(
            start_date=start_date,
            end_date=end_date,
            entries=entries,
            total_commits=len(commits),
            projects=projects
        )

        return report

    def format_markdown(self, report: WorkLogReport) -> str:
        """将报告格式化为 Markdown

        Args:
            report: 工作日志报告

        Returns:
            Markdown 格式字符串
        """
        lines = []

        # 标题
        title = f"# 工作日志 ({report.start_date.strftime('%Y-%m-%d')} ~ {report.end_date.strftime('%Y-%m-%d')})"
        lines.append(title)
        lines.append("")

        # 统计摘要
        lines.append("## 📊 统计摘要")
        lines.append("")
        lines.append(f"- **总提交数**: {report.total_commits}")
        lines.append(f"- **工作天数**: {len(report.entries)}")
        lines.append(f"- **涉及项目**: {len(report.projects)}个")
        lines.append(f"- **项目列表**: {', '.join(report.projects[:5])}{'...' if len(report.projects) > 5 else ''}")
        lines.append("")

        # 每日详情
        for entry in report.entries:
            lines.append(f"## 📅 {entry.date.strftime('%Y-%m-%d %A')}")
            lines.append("")

            # 提交记录
            lines.append("### 📝 提交记录")
            lines.append("")

            for commit in entry.commits:
                # 格式化提交信息
                formatted_commit = self._format_commit(commit)
                lines.append(formatted_commit)

            lines.append("")

            # 统计
            lines.append("### 📊 当日统计")
            lines.append("")
            lines.append(f"- 提交数: {len(entry.commits)}")

            if entry.projects:
                lines.append(f"- 涉及项目: {', '.join(entry.projects)}")

            if entry.summary:
                lines.append(f"- 主要工作: {entry.summary}")

            lines.append("")

        return "\n".join(lines)

    def _group_commits_by_date(self, commits: List[GitCommit]) -> Dict[datetime, List[GitCommit]]:
        """按日期分组提交

        Args:
            commits: 提交记录列表

        Returns:
            日期到提交列表的映射
        """
        grouped = defaultdict(list)

        for commit in commits:
            # 使用日期部分（不含时间）
            date_key = commit.committed_date.date()
            grouped[date_key].append(commit)

        # 转换为 datetime 并排序
        result = {}
        for date_key in sorted(grouped.keys(), reverse=True):
            result[datetime.combine(date_key, datetime.min.time())] = grouped[date_key]

        return result

    def _create_log_entry(self, date: datetime, commits: List[GitCommit]) -> WorkLogEntry:
        """创建日志条目

        Args:
            date: 日期
            commits: 该日期的提交列表

        Returns:
            工作日志条目
        """
        # 获取涉及的项目
        projects = list(set([c.project_name for c in commits if c.project_name]))

        # 生成摘要
        summary = self._generate_summary(commits)

        return WorkLogEntry(
            date=date,
            commits=commits,
            projects=projects,
            summary=summary
        )

    def _format_commit(self, commit: GitCommit) -> str:
        """格式化单条提交记录

        Args:
            commit: 提交记录

        Returns:
            格式化后的字符串
        """
        # 项目名称
        project = commit.project_name or "Unknown"

        # 提交标题
        title = commit.title.strip()

        # 简化提交信息
        # 移除常见的 commit prefix
        prefixes_to_remove = ["feat:", "fix:", "docs:", "style:", "refactor:", "test:", "chore:"]
        for prefix in prefixes_to_remove:
            if title.lower().startswith(prefix):
                title = title[len(prefix):].strip()
                break

        # 作者
        author = commit.author_name

        # 提交 ID（短）
        short_id = commit.short_id

        # 格式化
        formatted = f"- [{project}] {title} ({author}) [{short_id}]"

        return formatted

    def _generate_summary(self, commits: List[GitCommit]) -> str:
        """生成每日摘要

        Args:
            commits: 提交列表

        Returns:
            摘要文本
        """
        if not commits:
            return "无提交记录"

        # 统计任务类型
        task_types = defaultdict(int)
        for commit in commits:
            task_type = self._classify_task(commit)
            task_types[task_type] += 1

        # 生成摘要
        parts = []
        for task_type, count in sorted(task_types.items(), key=lambda x: -x[1]):
            if count > 0:
                parts.append(f"{task_type.value} {count}次")

        return "、".join(parts) if parts else "日常开发工作"

    def _classify_task(self, commit: GitCommit) -> TaskType:
        """根据提交信息分类任务类型

        Args:
            commit: 提交记录

        Returns:
            任务类型
        """
        title = commit.title.lower()
        message = commit.message.lower()

        # 修复
        if any(keyword in title or keyword in message for keyword in ["fix", "bug", "修复", "错误"]):
            return TaskType.BUGFIX

        # 文档
        if any(keyword in title or keyword in message for keyword in ["doc", "readme", "文档", "说明"]):
            return TaskType.DOCUMENTATION

        # 测试
        if any(keyword in title or keyword in message for keyword in ["test", "spec", "测试"]):
            return TaskType.TESTING

        # 重构
        if any(keyword in title or keyword in message for keyword in ["refactor", "重构", "优化"]):
            return TaskType.REFACTORING

        # 审查
        if any(keyword in title or keyword in message for keyword in ["review", "merge", "合并"]):
            return TaskType.REVIEW

        # 配置
        if any(keyword in title or keyword in message for keyword in ["config", "setting", "配置", "设置"]):
            return TaskType.OTHER

        # 默认为开发
        return TaskType.DEVELOPMENT

    def _get_unique_projects(self, commits: List[GitCommit]) -> List[str]:
        """获取唯一的项目列表

        Args:
            commits: 提交列表

        Returns:
            项目名称列表（去重）
        """
        projects = set()
        for commit in commits:
            if commit.project_name:
                projects.add(commit.project_name)

        return sorted(list(projects))

    def generate_simple_summary(self, commits: List[GitCommit]) -> str:
        """生成简单的文本摘要

        Args:
            commits: 提交列表

        Returns:
            摘要文本
        """
        if not commits:
            return "没有找到提交记录"

        total = len(commits)

        # 按项目统计
        project_stats = defaultdict(int)
        for commit in commits:
            if commit.project_name:
                project_stats[commit.project_name] += 1

        # 生成摘要
        lines = [
            f"总计 {total} 条提交记录",
            ""
        ]

        if project_stats:
            lines.append("按项目统计:")
            for project, count in sorted(project_stats.items(), key=lambda x: -x[1]):
                lines.append(f"  - {project}: {count}次")
            lines.append("")

        return "\n".join(lines)


# 全局单例
_summary_service: Optional[SummaryService] = None


def get_summary_service() -> SummaryService:
    """获取工作日志生成服务实例"""
    global _summary_service
    if _summary_service is None:
        _summary_service = SummaryService()
    return _summary_service
