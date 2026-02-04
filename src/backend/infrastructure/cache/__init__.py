"""
Cache Infrastructure

导出缓存抽象层和实现。
"""
from .base import CacheABC
from .memory_impl import MemoryCache

# 全局缓存实例
cache = MemoryCache()

__all__ = [
    "CacheABC",
    "cache",
    "MemoryCache"
]
