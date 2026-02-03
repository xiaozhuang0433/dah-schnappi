"""
Core Enumerations

定义系统使用的枚举类型。
"""
from enum import Enum


class PlatformType(str, Enum):
    """代码托管平台类型"""
    GITLAB = "gitlab"
    GITHUB = "github"


class CommitStatus(str, Enum):
    """提交状态"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class TaskType(str, Enum):
    """任务类型"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    MEETING = "meeting"
    REVIEW = "review"
    REFACTORING = "refactoring"
    BUGFIX = "bugfix"
    OTHER = "other"


class MessageRole(str, Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AttachmentType(str, Enum):
    """附件类型"""
    MARKDOWN = "markdown"
    TEXT = "text"
    JSON = "json"
    PDF = "pdf"
