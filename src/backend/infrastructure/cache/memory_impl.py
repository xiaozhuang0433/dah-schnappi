"""
In-Memory Cache Implementation

This module provides a memory-based cache implementation using cachetools,
with support for TTL (Time To Live) and maximum size limits.
"""
from typing import Optional, Any
from cachetools import TTLCache
from .base import CacheABC


class MemoryCache(CacheABC):
    """内存缓存实现（使用 cachetools）

    特性：
    - 自动过期（TTL）
    - 最大容量限制（LRU 淘汰）
    - 线程安全
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """初始化内存缓存

        Args:
            max_size: 最大缓存条目数，默认 1000
            default_ttl: 默认过期时间（秒），默认 3600（1小时）
        """
        self.cache = TTLCache(maxsize=max_size, ttl=default_ttl)
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        return self.cache.get(key)

    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """设置缓存

        注意：TTL 由 TTLCache 统一管理，不支持单独设置
        """
        self.cache[key] = value

    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """清空所有缓存"""
        self.cache.clear()

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return key in self.cache

    def get_many(self, keys: list[str]) -> dict[str, Any]:
        """批量获取缓存"""
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def set_many(self, mapping: dict[str, Any], ttl: int = None) -> None:
        """批量设置缓存"""
        for key, value in mapping.items():
            self.set(key, value, ttl)

    def delete_many(self, keys: list[str]) -> int:
        """批量删除缓存"""
        count = 0
        for key in keys:
            if self.delete(key):
                count += 1
        return count

    def incr(self, key: str, delta: int = 1) -> int:
        """递增计数器"""
        current = self.get(key) or 0
        new_value = current + delta
        self.set(key, new_value)
        return new_value

    def decr(self, key: str, delta: int = 1) -> int:
        """递减计数器"""
        current = self.get(key) or 0
        new_value = current - delta
        self.set(key, new_value)
        return new_value

    def size(self) -> int:
        """获取当前缓存大小"""
        return len(self.cache)

    def keys(self) -> list[str]:
        """获取所有缓存键"""
        return list(self.cache.keys())

    def values(self) -> list[Any]:
        """获取所有缓存值"""
        return list(self.cache.values())

    def items(self) -> list[tuple[str, Any]]:
        """获取所有缓存键值对"""
        return list(self.cache.items())
