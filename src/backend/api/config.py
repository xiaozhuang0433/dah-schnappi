"""
Configuration API Router

用户配置相关的 API 路由。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from src.infrastructure.database.models import (
    UserConfigResponse,
    UserConfigUpdate,
    GitLabConfigUpdate,
    GitHubConfigUpdate
)
from src.auth.dependencies import get_current_user, get_current_user_id
from src.services.config_service import ConfigService
from src.utils.logger import get_logger


router = APIRouter(prefix="/api/config", tags=["Configuration"])
logger = get_logger(__name__)


@router.get("", response_model=UserConfigResponse)
async def get_config(
    current_user_id: int = Depends(get_current_user_id)
) -> UserConfigResponse:
    """获取当前用户配置

    Returns:
        用户配置对象（敏感信息已脱敏）
    """
    config = await ConfigService.get_by_user_id(current_user_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found. Please create a configuration first."
        )

    # 响应模型会自动脱敏敏感字段
    return UserConfigResponse(
        id=config.id,
        user_id=config.user_id,
        gitlab_url=config.gitlab_url,
        gitlab_token=config.gitlab_token,
        github_username=config.github_username,
        github_token=config.github_token,
        default_platform=config.default_platform,
        include_branches=config.include_branches,
        created_at=config.created_at,
        updated_at=config.updated_at
    )


@router.put("")
async def update_config(
    config_update: UserConfigUpdate,
    current_user_id: int = Depends(get_current_user_id)
) -> Dict[str, str]:
    """更新用户配置

    支持部分更新，只更新提供的字段。

    Args:
        config_update: 配置更新数据
        current_user_id: 当前用户 ID

    Returns:
        成功消息
    """
    updated = await ConfigService.update(current_user_id, config_update)

    return {
        "status": "success",
        "message": "Configuration updated successfully"
    }


@router.patch("/gitlab")
async def update_gitlab_config(
    gitlab_config: GitLabConfigUpdate,
    current_user_id: int = Depends(get_current_user_id)
) -> Dict[str, str]:
    """更新 GitLab 配置

    Args:
        gitlab_config: GitLab 配置
        current_user_id: 当前用户 ID

    Returns:
        成功消息
    """
    await ConfigService.update_gitlab(current_user_id, gitlab_config)

    return {
        "status": "success",
        "message": "GitLab configuration updated successfully"
    }


@router.patch("/github")
async def update_github_config(
    github_config: GitHubConfigUpdate,
    current_user_id: int = Depends(get_current_user_id)
) -> Dict[str, str]:
    """更新 GitHub 配置

    Args:
        github_config: GitHub 配置
        current_user_id: 当前用户 ID

    Returns:
        成功消息
    """
    await ConfigService.update_github(current_user_id, github_config)

    return {
        "status": "success",
        "message": "GitHub configuration updated successfully"
    }


@router.delete("")
async def delete_config(
    current_user_id: int = Depends(get_current_user_id)
) -> Dict[str, str]:
    """删除用户配置

    Args:
        current_user_id: 当前用户 ID

    Returns:
        成功消息
    """
    await ConfigService.delete(current_user_id)

    return {
        "status": "success",
        "message": "Configuration deleted successfully"
    }


@router.post("/reset")
async def reset_config(
    current_user_id: int = Depends(get_current_user_id)
) -> Dict[str, str]:
    """重置用户配置

    删除现有配置，创建新的空配置。

    Args:
        current_user_id: 当前用户 ID

    Returns:
        成功消息
    """
    await ConfigService.delete(current_user_id)

    return {
        "status": "success",
        "message": "Configuration reset successfully"
    }
