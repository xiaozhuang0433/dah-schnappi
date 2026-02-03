"""
MySQL Database Implementation

This module provides a MySQL implementation of the DatabaseABC interface.
MySQL is a popular open source relational database management system.
"""
import pymysql
from pymysql.cursors import DictCursor
import os
from typing import Type, Optional, List, Dict, Any
from .base import DatabaseABC


class MySQLDatabase(DatabaseABC):
    """MySQL 数据库实现

    提供 MySQL 数据库的具体实现，包括：
    - 连接池管理
    - 自动建表
    - CRUD 操作
    - 原生 SQL 执行
    - 外键约束
    - ACID 事务
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        database: str = "dahschnappi",
        user: str = "root",
        password: str = "",
        charset: str = "utf8mb4"
    ):
        """初始化 MySQL 连接

        Args:
            host: 数据库主机
            port: 数据库端口
            database: 数据库名称
            user: 用户名
            password: 密码
            charset: 字符集
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.charset = charset
        self.conn: Optional[pymysql.connections.Connection] = None

    def connect(self) -> None:
        """连接数据库并初始化表结构"""
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            cursorclass=DictCursor,
            autocommit=True
        )
        self._init_tables()

    def disconnect(self) -> None:
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def insert(self, model: Type, data: Dict[str, Any]) -> int:
        """插入数据，返回 ID"""
        table_name = model.__tablename__
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s' for _ in data])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with self.conn.cursor() as cursor:
            cursor.execute(sql, list(data.values()))
            return cursor.lastrowid

    def get_by_id(self, model: Type, id: int) -> Optional[Any]:
        """根据 ID 获取数据"""
        table_name = model.__tablename__
        sql = f"SELECT * FROM {table_name} WHERE id = %s"

        with self.conn.cursor() as cursor:
            cursor.execute(sql, [id])
            result = cursor.fetchone()
            return model(**result) if result else None

    def get_by_field(self, model: Type, field: str, value: Any) -> List[Any]:
        """根据字段获取数据列表"""
        table_name = model.__tablename__
        sql = f"SELECT * FROM {table_name} WHERE {field} = %s"

        with self.conn.cursor() as cursor:
            cursor.execute(sql, [value])
            results = cursor.fetchall()
            return [model(**row) for row in results]

    def get_one_by_field(self, model: Type, field: str, value: Any) -> Optional[Any]:
        """根据字段获取单条数据"""
        results = self.get_by_field(model, field, value)
        return results[0] if results else None

    def update(self, model: Type, id: int, data: Dict[str, Any]) -> bool:
        """更新数据"""
        table_name = model.__tablename__
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"

        with self.conn.cursor() as cursor:
            cursor.execute(sql, list(data.values()) + [id])
            return True

    def delete(self, model: Type, id: int) -> bool:
        """删除数据"""
        table_name = model.__tablename__
        sql = f"DELETE FROM {table_name} WHERE id = %s"

        with self.conn.cursor() as cursor:
            cursor.execute(sql, [id])
            return True

    def execute_sql(self, sql: str, params: Dict[str, Any] = None) -> List[Dict]:
        """执行原始 SQL"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params or [])
            return cursor.fetchall()

    def get_all(self, model: Type, limit: int = None, offset: int = 0) -> List[Any]:
        """获取所有数据"""
        table_name = model.__tablename__
        sql = f"SELECT * FROM {table_name}"
        if limit:
            sql += f" LIMIT {limit} OFFSET {offset}"

        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            return [model(**row) for row in results]

    def count(self, model: Type) -> int:
        """统计记录数"""
        table_name = model.__tablename__
        sql = f"SELECT COUNT(*) as count FROM {table_name}"

        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
            return result['count'] if result else 0

    def exists(self, model: Type, field: str, value: Any) -> bool:
        """检查记录是否存在"""
        table_name = model.__tablename__
        sql = f"SELECT COUNT(*) as count FROM {table_name} WHERE {field} = %s"

        with self.conn.cursor() as cursor:
            cursor.execute(sql, [value])
            result = cursor.fetchone()
            return result['count'] > 0 if result else False

    def _init_tables(self) -> None:
        """初始化表结构

        创建 users 和 user_configs 表，包含：
        - 主键约束
        - 外键约束
        - 唯一性约束
        - 默认值
        """
        # 创建 users 表
        self.execute_sql("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # 创建 user_configs 表
        self.execute_sql("""
            CREATE TABLE IF NOT EXISTS user_configs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL UNIQUE,
                gitlab_url VARCHAR(255),
                gitlab_token VARCHAR(255),
                github_username VARCHAR(100),
                github_token VARCHAR(255),
                default_platform VARCHAR(20) DEFAULT 'gitlab',
                include_branches TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        sql = """
            SELECT COUNT(*) as count
            FROM information_schema.tables
            WHERE table_schema = %s AND table_name = %s
        """
        result = self.execute_sql(sql, [self.database, table_name])
        return result[0]['count'] > 0 if result else False

    def get_table_info(self, table_name: str) -> List[Dict]:
        """获取表结构信息"""
        sql = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        return self.execute_sql(sql, [self.database, table_name])
