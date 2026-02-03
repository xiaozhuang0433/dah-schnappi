"""
PostgreSQL Database Implementation

This module provides a PostgreSQL implementation of the DatabaseABC interface.
PostgreSQL is a powerful, open source object-relational database system.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool
import os
from typing import Type, Optional, List, Dict, Any
from .base import DatabaseABC


class PostgreSQLDatabase(DatabaseABC):
    """PostgreSQL 数据库实现

    提供 PostgreSQL 数据库的具体实现，包括：
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
        port: int = 5432,
        database: str = "dahschnappi",
        user: str = "postgres",
        password: str = "",
        pool_size: int = 5
    ):
        """初始化 PostgreSQL 连接

        Args:
            host: 数据库主机
            port: 数据库端口
            database: 数据库名称
            user: 用户名
            password: 密码
            pool_size: 连接池大小
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.pool_size = pool_size
        self.pool: Optional[psycopg2.pool.SimpleConnectionPool] = None

    def _get_url(self) -> str:
        """获取数据库连接 URL"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def connect(self) -> None:
        """连接数据库并初始化表结构"""
        self.pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=self.pool_size,
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
            cursor_factory=RealDictCursor
        )
        self._init_tables()

    def disconnect(self) -> None:
        """断开数据库连接"""
        if self.pool:
            self.pool.closeall()
            self.pool = None

    def _get_connection(self):
        """从连接池获取连接"""
        if not self.pool:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.pool.getconn()

    def _put_connection(self, conn):
        """归还连接到连接池"""
        if self.pool:
            self.pool.putconn(conn)

    def insert(self, model: Type, data: Dict[str, Any]) -> int:
        """插入数据，返回 ID"""
        table_name = model.__tablename__
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s' for _ in data])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING id"

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, list(data.values()))
            result = cursor.fetchone()
            conn.commit()
            return result['id'] if result else None
        finally:
            self._put_connection(conn)

    def get_by_id(self, model: Type, id: int) -> Optional[Any]:
        """根据 ID 获取数据"""
        table_name = model.__tablename__
        sql = f"SELECT * FROM {table_name} WHERE id = %s"

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, [id])
            result = cursor.fetchone()
            return model(**dict(result)) if result else None
        finally:
            self._put_connection(conn)

    def get_by_field(self, model: Type, field: str, value: Any) -> List[Any]:
        """根据字段获取数据列表"""
        table_name = model.__tablename__
        sql = f"SELECT * FROM {table_name} WHERE {field} = %s"

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, [value])
            results = cursor.fetchall()
            return [model(**dict(row)) for row in results]
        finally:
            self._put_connection(conn)

    def get_one_by_field(self, model: Type, field: str, value: Any) -> Optional[Any]:
        """根据字段获取单条数据"""
        results = self.get_by_field(model, field, value)
        return results[0] if results else None

    def update(self, model: Type, id: int, data: Dict[str, Any]) -> bool:
        """更新数据"""
        table_name = model.__tablename__
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, list(data.values()) + [id])
            conn.commit()
            return True
        finally:
            self._put_connection(conn)

    def delete(self, model: Type, id: int) -> bool:
        """删除数据"""
        table_name = model.__tablename__
        sql = f"DELETE FROM {table_name} WHERE id = %s"

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, [id])
            conn.commit()
            return True
        finally:
            self._put_connection(conn)

    def execute_sql(self, sql: str, params: Dict[str, Any] = None) -> List[Dict]:
        """执行原始 SQL"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params or [])
            return [dict(row) for row in cursor.fetchall()]
        finally:
            self._put_connection(conn)

    def get_all(self, model: Type, limit: int = None, offset: int = 0) -> List[Any]:
        """获取所有数据"""
        table_name = model.__tablename__
        sql = f"SELECT * FROM {table_name}"
        if limit:
            sql += f" LIMIT {limit} OFFSET {offset}"

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            return [model(**dict(row)) for row in results]
        finally:
            self._put_connection(conn)

    def count(self, model: Type) -> int:
        """统计记录数"""
        table_name = model.__tablename__
        sql = f"SELECT COUNT(*) FROM {table_name}"

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            return result['count'] if result else 0
        finally:
            self._put_connection(conn)

    def exists(self, model: Type, field: str, value: Any) -> bool:
        """检查记录是否存在"""
        table_name = model.__tablename__
        sql = f"SELECT COUNT(*) FROM {table_name} WHERE {field} = %s"

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, [value])
            result = cursor.fetchone()
            return result['count'] > 0 if result else False
        finally:
            self._put_connection(conn)

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
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建 user_configs 表
        self.execute_sql("""
            CREATE TABLE IF NOT EXISTS user_configs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE,
                gitlab_url VARCHAR(255),
                gitlab_token VARCHAR(255),
                github_username VARCHAR(100),
                github_token VARCHAR(255),
                default_platform VARCHAR(20) DEFAULT 'gitlab',
                include_branches BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 创建 indexes
        self.execute_sql("""
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
        """)
        self.execute_sql("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)
        self.execute_sql("""
            CREATE INDEX IF NOT EXISTS idx_user_configs_user_id ON user_configs(user_id)
        """)

    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        sql = """
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = %s
        """
        result = self.execute_sql(sql, [table_name])
        return result[0]['count'] > 0 if result else False

    def get_table_info(self, table_name: str) -> List[Dict]:
        """获取表结构信息"""
        sql = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """
        return self.execute_sql(sql, [table_name])
