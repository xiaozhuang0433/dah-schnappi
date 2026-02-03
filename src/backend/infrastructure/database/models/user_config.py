"""
User Configuration Data Model

定义用户配置相关的数据模型，包括 GitLab 和 GitHub 配置。
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class PlatformType(str, Enum):
    """支持的代码托管平台"""
    gitlab = "gitlab"
    github = "github"


class UserConfigBase(BaseModel):
    """用户配置基础模型"""
    # GitLab 配置
    gitlab_url: Optional[str] = Field(None, description="GitLab 服务器地址")
    gitlab_token: Optional[str] = Field(None, description="GitLab 访问令牌")

    # GitHub 配置
    github_username: Optional[str] = Field(None, description="GitHub 用户名")
    github_token: Optional[str] = Field(None, description="GitHub 访问令牌")

    # 其他配置
    default_platform: PlatformType = Field(
        default=PlatformType.gitlab,
        description="默认平台"
    )
    include_branches: bool = Field(
        default=False,
        description="是否包含分支信息"
    )


class UserConfigCreate(UserConfigBase):
    """用户配置创建模型"""
    pass


class UserConfigUpdate(BaseModel):
    """用户配置更新模型（所有字段可选）"""
    gitlab_url: Optional[str] = None
    gitlab_token: Optional[str] = None
    github_username: Optional[str] = None
    github_token: Optional[str] = None
    default_platform: Optional[PlatformType] = None
    include_branches: Optional[bool] = None


class GitLabConfigUpdate(BaseModel):
    """GitLab 配置更新模型"""
    gitlab_url: str = Field(..., description="GitLab 服务器地址")
    gitlab_token: str = Field(..., description="GitLab 访问令牌")


class GitHubConfigUpdate(BaseModel):
    """GitHub 配置更新模型"""
    github_username: str = Field(..., description="GitHub 用户名")
    github_token: str = Field(..., description="GitHub 访问令牌")


class UserConfigInDB(UserConfigBase):
    """数据库中的用户配置模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    # ORM 兼容
    __tablename__ = "user_configs"

    class Config:
        from_attributes = True


class UserConfigResponse(UserConfigBase):
    """用户配置响应模型（敏感信息脱敏）"""
    id: int
    user_id: int
    gitlab_token: Optional[str] = Field(None, description="GitLab 令牌（脱敏）")
    github_token: Optional[str] = Field(None, description="GitHub 令牌（脱敏）")
    created_at: datetime
    updated_at: datetime

    @validator('gitlab_token', pre=True)
    def mask_gitlab_token(cls, v):
        """脱敏 GitLab Token"""
        if v and len(v) > 8:
            return f"{v[:8]}****"
        return "****"

    @validator('github_token', pre=True)
    def mask_github_token(cls, v):
        """脱敏 GitHub Token"""
        if v and len(v) > 8:
            return f"{v[:8]}****"
        return "****"

    class Config:
        from_attributes = True
