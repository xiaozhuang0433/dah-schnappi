"""
Application Settings

使用 Pydantic Settings 管理应用配置。
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置类

    从环境变量和配置文件中读取配置。
    """

    # 应用配置
    APP_NAME: str = "DahSchnappi"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 数据库配置
    DATABASE_IMPLEMENTATION: str = "sqlite"  # 可选: sqlite, postgresql, mysql

    # SQLite 配置
    SQLITE_PATH: str = "data/dahschnappi.db"

    # PostgreSQL 配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DATABASE: str = "dahschnappi"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""

    # MySQL 配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "dahschnappi"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_CHARSET: str = "utf8mb4"

    # 缓存配置
    CACHE_IMPLEMENTATION: str = "memory"  # 可选: memory, redis
    CACHE_MAX_SIZE: int = 1000
    CACHE_DEFAULT_TTL: int = 3600  # 1小时

    # 加密配置
    ENCRYPTION_KEY: Optional[str] = None

    # JWT 认证配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # CORS 配置
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # LLM 配置
    LLM_PROVIDER: str = "claude"  # 可选: claude, openai
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    LLM_MODEL: str = "claude-sonnet-4-5-20250929"  # 默认模型
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/worklog.log"

    model_config = SettingsConfigDict(
        env_file=[".env", "../.env", "../../.env"],  # 依次查找：当前目录、父目录、祖父目录
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def get_encryption_key(self) -> str:
        """获取加密密钥

        如果环境变量中没有设置，使用默认密钥（仅开发环境）。
        """
        if self.ENCRYPTION_KEY:
            return self.ENCRYPTION_KEY

        # 开发环境使用默认密钥
        if self.DEBUG:
            return "a" * 44  # 32字节 base64 编码后的长度

        raise ValueError("ENCRYPTION_KEY must be set in production")

    def get_llm_api_key(self) -> str:
        """获取 LLM API 密钥"""
        if self.LLM_PROVIDER == "claude":
            if not self.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY must be set for Claude")
            return self.ANTHROPIC_API_KEY
        elif self.LLM_PROVIDER == "openai":
            if not self.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY must be set for OpenAI")
            return self.OPENAI_API_KEY
        else:
            raise ValueError(f"Unsupported LLM provider: {self.LLM_PROVIDER}")


# 全局配置实例
settings = Settings()
