"""
Database Infrastructure

导出数据库抽象层和实现。
支持：SQLite (默认), PostgreSQL, MySQL
"""
from .base import DatabaseABC
from .sqlite_impl import SQLiteDatabase
from .postgres_impl import PostgreSQLDatabase
from .mysql_impl import MySQLDatabase
from .factory import db
from .models import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    UserLogin,
    UserConfigBase,
    UserConfigCreate,
    UserConfigUpdate,
    GitLabConfigUpdate,
    GitHubConfigUpdate,
    UserConfigInDB,
    UserConfigResponse,
    PlatformType
)

__all__ = [
    "DatabaseABC",
    "db",
    "SQLiteDatabase",
    "PostgreSQLDatabase",
    "MySQLDatabase",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "UserLogin",
    "UserConfigBase",
    "UserConfigCreate",
    "UserConfigUpdate",
    "GitLabConfigUpdate",
    "GitHubConfigUpdate",
    "UserConfigInDB",
    "UserConfigResponse",
    "PlatformType"
]
