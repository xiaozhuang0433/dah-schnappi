"""
Core Data Models

定义系统核心数据模型。
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .enums import PlatformType, TaskType, MessageRole, AttachmentType


class GitCommit(BaseModel):
    """Git 提交记录模型"""
    id: str = Field(..., description="提交 ID")
    short_id: str = Field(..., description="短提交 ID")
    title: str = Field(..., description="提交标题")
    message: str = Field(..., description="提交信息")
    author_name: str = Field(..., description="作者姓名")
    author_email: str = Field(..., description="作者邮箱")
    authored_date: datetime = Field(..., description="提交时间")
    committed_date: datetime = Field(..., description="提交时间")
    web_url: str = Field(..., description="提交 URL")
    project_id: Optional[int] = Field(None, description="项目 ID")
    project_name: Optional[str] = Field(None, description="项目名称")
    branch: Optional[str] = Field(None, description="分支名称")
    diff: Optional[str] = Field(None, description="代码差异")

    class Config:
        from_attributes = True


class GitProject(BaseModel):
    """Git 项目模型"""
    id: int = Field(..., description="项目 ID")
    name: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    web_url: str = Field(..., description="项目 URL")
    default_branch: str = Field(default="main", description="默认分支")
    created_at: datetime = Field(..., description="创建时间")
    last_activity_at: datetime = Field(..., description="最后活动时间")

    class Config:
        from_attributes = True


class WorkLogEntry(BaseModel):
    """工作日志条目模型"""
    date: datetime = Field(..., description="日期")
    commits: List[GitCommit] = Field(default_factory=list, description="提交记录")
    task_type: Optional[TaskType] = Field(None, description="任务类型")
    summary: Optional[str] = Field(None, description="摘要")
    projects: List[str] = Field(default_factory=list, description="涉及的项目")

    class Config:
        from_attributes = True


class WorkLogReport(BaseModel):
    """工作日志报告模型"""
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    entries: List[WorkLogEntry] = Field(default_factory=list, description="日志条目")
    total_commits: int = Field(default=0, description="总提交数")
    projects: List[str] = Field(default_factory=list, description="涉及项目")
    summary: Optional[str] = Field(None, description="总体摘要")

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    """聊天消息模型"""
    id: str = Field(..., description="消息 ID")
    role: MessageRole = Field(..., description="角色")
    content: str = Field(..., description="消息内容")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    class Config:
        from_attributes = True


class Attachment(BaseModel):
    """附件模型"""
    type: AttachmentType = Field(..., description="附件类型")
    filename: str = Field(..., description="文件名")
    content: str = Field(..., description="内容（Base64 编码）")
    size: Optional[int] = Field(None, description="文件大小（字节）")

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: ChatMessage = Field(..., description="回复消息")
    attachments: List[Attachment] = Field(default_factory=list, description="附件列表")

    class Config:
        from_attributes = True


class MCPToolCall(BaseModel):
    """MCP 工具调用模型"""
    name: str = Field(..., description="工具名称")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="工具参数")
    result: Optional[Any] = Field(None, description="执行结果")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: Optional[float] = Field(None, description="执行时间（秒）")

    class Config:
        from_attributes = True
