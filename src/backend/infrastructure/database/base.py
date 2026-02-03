"""
Database Abstraction Layer

This module provides an abstract base class for database operations,
allowing for pluggable database implementations (DuckDB, PostgreSQL, etc.).
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any

T = TypeVar('T')


class DatabaseABC(ABC):
    """数据库抽象基类

    定义数据库操作的通用接口，所有数据库实现必须继承此类。
    支持同步和异步操作模式。
    """

    @abstractmethod
    def connect(self) -> None:
        """连接数据库"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """断开数据库连接"""
        pass

    @abstractmethod
    def insert(self, model: Type[T], data: Dict[str, Any]) -> int:
        """插入数据，返回 ID

        Args:
            model: 数据模型类
            data: 要插入的数据字典

        Returns:
            新插入记录的 ID
        """
        pass

    @abstractmethod
    def get_by_id(self, model: Type[T], id: int) -> Optional[T]:
        """根据 ID 获取数据

        Args:
            model: 数据模型类
            id: 记录 ID

        Returns:
            模型实例，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def get_by_field(self, model: Type[T], field: str, value: Any) -> List[T]:
        """根据字段获取数据列表

        Args:
            model: 数据模型类
            field: 字段名
            value: 字段值

        Returns:
            模型实例列表
        """
        pass

    @abstractmethod
    def get_one_by_field(self, model: Type[T], field: str, value: Any) -> Optional[T]:
        """根据字段获取单条数据

        Args:
            model: 数据模型类
            field: 字段名
            value: 字段值

        Returns:
            模型实例，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def update(self, model: Type[T], id: int, data: Dict[str, Any]) -> bool:
        """更新数据

        Args:
            model: 数据模型类
            id: 记录 ID
            data: 要更新的数据字典

        Returns:
            是否成功更新
        """
        pass

    @abstractmethod
    def delete(self, model: Type[T], id: int) -> bool:
        """删除数据

        Args:
            model: 数据模型类
            id: 记录 ID

        Returns:
            是否成功删除
        """
        pass

    @abstractmethod
    def execute_sql(self, sql: str, params: Dict[str, Any] = None) -> List[Dict]:
        """执行原始 SQL

        Args:
            sql: SQL 语句
            params: SQL 参数

        Returns:
            查询结果列表
        """
        pass

    @abstractmethod
    def get_all(self, model: Type[T], limit: int = None, offset: int = 0) -> List[T]:
        """获取所有数据

        Args:
            model: 数据模型类
            limit: 限制返回数量
            offset: 偏移量

        Returns:
            模型实例列表
        """
        pass

    @abstractmethod
    def count(self, model: Type[T]) -> int:
        """统计记录数

        Args:
            model: 数据模型类

        Returns:
            记录总数
        """
        pass

    @abstractmethod
    def exists(self, model: Type[T], field: str, value: Any) -> bool:
        """检查记录是否存在

        Args:
            model: 数据模型类
            field: 字段名
            value: 字段值

        Returns:
            记录是否存在
        """
        pass
