"""
Core Package

导出核心模块。
"""
from .base import (
    CommitFetcherABC,
    WorkLogGeneratorABC,
    CommitAnalyzerABC
)
from .models import (
    GitCommit,
    GitProject,
    WorkLogEntry,
    WorkLogReport,
    ChatMessage,
    Attachment,
    ChatResponse,
    MCPToolCall
)
from .enums import (
    PlatformType,
    CommitStatus,
    TaskType,
    MessageRole,
    AttachmentType
)
from .fetchers import (
    GitLabFetcher,
    GitHubFetcher
)

__all__ = [
    # Base
    "CommitFetcherABC",
    "WorkLogGeneratorABC",
    "CommitAnalyzerABC",
    # Models
    "GitCommit",
    "GitProject",
    "WorkLogEntry",
    "WorkLogReport",
    "ChatMessage",
    "Attachment",
    "ChatResponse",
    "MCPToolCall",
    # Enums
    "PlatformType",
    "CommitStatus",
    "TaskType",
    "MessageRole",
    "AttachmentType",
    # Fetchers
    "GitLabFetcher",
    "GitHubFetcher"
]
