"""
Cache Infrastructure

导出缓存抽象层和实现。
"""
from .base import CacheABC
from .memory_impl import MemoryCache

__all__ = [
    "CacheABC",
    "MemoryCache"
]
