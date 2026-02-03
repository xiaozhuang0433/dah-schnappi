"""
Cache Abstraction Layer

This module provides an abstract base class for cache operations,
allowing for pluggable cache implementations (Memory, Redis, etc.).
"""
from abc import ABC, abstractmethod
from typing import Optional, Any


class CacheABC(ABC):
    """缓存抽象基类

    定义缓存操作的通用接口，所有缓存实现必须继承此类。
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """设置缓存

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 表示永不过期
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存

        Args:
            key: 缓存键

        Returns:
            是否成功删除
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """清空所有缓存"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """检查键是否存在

        Args:
            key: 缓存键

        Returns:
            键是否存在
        """
        pass

    @abstractmethod
    def get_many(self, keys: list[str]) -> dict[str, Any]:
        """批量获取缓存

        Args:
            keys: 缓存键列表

        Returns:
            键值对字典
        """
        pass

    @abstractmethod
    def set_many(self, mapping: dict[str, Any], ttl: int = None) -> None:
        """批量设置缓存

        Args:
            mapping: 键值对字典
            ttl: 过期时间（秒）
        """
        pass

    @abstractmethod
    def delete_many(self, keys: list[str]) -> int:
        """批量删除缓存

        Args:
            keys: 缓存键列表

        Returns:
            成功删除的数量
        """
        pass

    @abstractmethod
    def incr(self, key: str, delta: int = 1) -> int:
        """递增计数器

        Args:
            key: 缓存键
            delta: 递增量

        Returns:
            递增后的值
        """
        pass

    @abstractmethod
    def decr(self, key: str, delta: int = 1) -> int:
        """递减计数器

        Args:
            key: 缓存键
            delta: 递减量

        Returns:
            递减后的值
        """
        pass
