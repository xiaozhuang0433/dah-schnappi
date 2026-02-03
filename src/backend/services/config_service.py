"""
User Configuration Service

用户配置管理服务。
"""
from typing import Optional
from fastapi import HTTPException, status
from src.infrastructure.database import db, UserConfigInDB, UserConfigUpdate, GitLabConfigUpdate, GitHubConfigUpdate
from src.infrastructure.cache import cache
from src.utils.crypto import get_crypto
from src.utils.logger import get_logger


logger = get_logger(__name__)
crypto = get_crypto()


class ConfigService:
    """用户配置服务"""

    CACHE_PREFIX = "user_config"
    CACHE_TTL = 3600  # 1小时

    @staticmethod
    def _get_cache_key(user_id: int) -> str:
        """获取缓存键"""
        return f"{ConfigService.CACHE_PREFIX}:{user_id}"

    @staticmethod
    async def get_by_user_id(user_id: int) -> Optional[UserConfigInDB]:
        """根据用户 ID 获取配置

        Args:
            user_id: 用户 ID

        Returns:
            用户配置对象，如果不存在则返回 None
        """
        # 先尝试从缓存获取
        cache_key = ConfigService._get_cache_key(user_id)
        cached_config = await cache.get(cache_key)
        if cached_config:
            return cached_config

        # 从数据库获取
        config = await db.get_one_by_field(UserConfigInDB, "user_id", user_id)

        if config:
            # 解密敏感字段
            if config.gitlab_token:
                try:
                    config.gitlab_token = crypto.decrypt(config.gitlab_token)
                except Exception as e:
                    logger.warning(f"Failed to decrypt gitlab_token for user {user_id}: {str(e)}")

            if config.github_token:
                try:
                    config.github_token = crypto.decrypt(config.github_token)
                except Exception as e:
                    logger.warning(f"Failed to decrypt github_token for user {user_id}: {str(e)}")

            # 缓存配置（注意：缓存的是解密后的）
            await cache.set(cache_key, config, ttl=ConfigService.CACHE_TTL)

        return config

    @staticmethod
    async def create(user_id: int, config_data: dict) -> UserConfigInDB:
        """创建用户配置

        Args:
            user_id: 用户 ID
            config_data: 配置数据

        Returns:
            创建的配置对象
        """
        # 检查是否已存在
        existing = await db.get_one_by_field(UserConfigInDB, "user_id", user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User configuration already exists"
            )

        # 加密敏感字段
        encrypted_data = crypto.encrypt_dict(config_data, ["gitlab_token", "github_token"])
        encrypted_data["user_id"] = user_id

        # 插入数据库
        config_id = await db.insert(UserConfigInDB, encrypted_data)

        # 清除缓存（如果有的话）
        await cache.delete(ConfigService._get_cache_key(user_id))

        # 返回解密后的配置
        config = await db.get_by_id(UserConfigInDB, config_id)
        config.gitlab_token = config_data.get("gitlab_token")
        config.github_token = config_data.get("github_token")

        logger.info(f"Created configuration for user {user_id}")

        return config

    @staticmethod
    async def update(user_id: int, config_update: UserConfigUpdate) -> UserConfigInDB:
        """更新用户配置

        Args:
            user_id: 用户 ID
            config_update: 配置更新数据

        Returns:
            更新后的配置对象

        Raises:
            HTTPException: 如果配置不存在
        """
        # 获取现有配置
        config = await db.get_one_by_field(UserConfigInDB, "user_id", user_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User configuration not found"
            )

        # 准备更新数据
        update_data = {}
        if config_update.gitlab_url is not None:
            update_data["gitlab_url"] = config_update.gitlab_url
        if config_update.gitlab_token is not None:
            update_data["gitlab_token"] = crypto.encrypt(config_update.gitlab_token)
        if config_update.github_username is not None:
            update_data["github_username"] = config_update.github_username
        if config_update.github_token is not None:
            update_data["github_token"] = crypto.encrypt(config_update.github_token)
        if config_update.default_platform is not None:
            update_data["default_platform"] = config_update.default_platform.value
        if config_update.include_branches is not None:
            update_data["include_branches"] = config_update.include_branches

        # 更新数据库
        await db.update(UserConfigInDB, config.id, update_data)

        # 清除缓存
        await cache.delete(ConfigService._get_cache_key(user_id))

        # 返回更新后的配置（解密）
        updated = await db.get_by_id(UserConfigInDB, config.id)
        if updated.gitlab_token:
            try:
                updated.gitlab_token = crypto.decrypt(updated.gitlab_token)
            except Exception:
                pass
        if updated.github_token:
            try:
                updated.github_token = crypto.decrypt(updated.github_token)
            except Exception:
                pass

        logger.info(f"Updated configuration for user {user_id}")

        return updated

    @staticmethod
    async def update_gitlab(user_id: int, gitlab_config: GitLabConfigUpdate) -> UserConfigInDB:
        """更新 GitLab 配置

        Args:
            user_id: 用户 ID
            gitlab_config: GitLab 配置

        Returns:
            更新后的配置对象
        """
        # 获取现有配置
        config = await db.get_one_by_field(UserConfigInDB, "user_id", user_id)

        update_data = {
            "gitlab_url": gitlab_config.gitlab_url,
            "gitlab_token": crypto.encrypt(gitlab_config.gitlab_token)
        }

        if config:
            await db.update(UserConfigInDB, config.id, update_data)
        else:
            update_data["user_id"] = user_id
            await db.insert(UserConfigInDB, update_data)

        # 清除缓存
        await cache.delete(ConfigService._get_cache_key(user_id))

        logger.info(f"Updated GitLab configuration for user {user_id}")

        return await ConfigService.get_by_user_id(user_id)

    @staticmethod
    async def update_github(user_id: int, github_config: GitHubConfigUpdate) -> UserConfigInDB:
        """更新 GitHub 配置

        Args:
            user_id: 用户 ID
            github_config: GitHub 配置

        Returns:
            更新后的配置对象
        """
        # 获取现有配置
        config = await db.get_one_by_field(UserConfigInDB, "user_id", user_id)

        update_data = {
            "github_username": github_config.github_username,
            "github_token": crypto.encrypt(github_config.github_token)
        }

        if config:
            await db.update(UserConfigInDB, config.id, update_data)
        else:
            update_data["user_id"] = user_id
            await db.insert(UserConfigInDB, update_data)

        # 清除缓存
        await cache.delete(ConfigService._get_cache_key(user_id))

        logger.info(f"Updated GitHub configuration for user {user_id}")

        return await ConfigService.get_by_user_id(user_id)

    @staticmethod
    async def delete(user_id: int) -> bool:
        """删除用户配置

        Args:
            user_id: 用户 ID

        Returns:
            是否成功删除
        """
        config = await db.get_one_by_field(UserConfigInDB, "user_id", user_id)
        if config:
            await db.delete(UserConfigInDB, config.id)
            await cache.delete(ConfigService._get_cache_key(user_id))
            logger.info(f"Deleted configuration for user {user_id}")
            return True
        return False
