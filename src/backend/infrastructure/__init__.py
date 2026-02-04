"""
Infrastructure Package

提供数据库和缓存的抽象层及实现。
"""
from .database import DatabaseABC, db
from .cache import CacheABC, cache

__all__ = [
    "DatabaseABC",
    "db",
    "CacheABC",
    "cache"
]
