"""
DuckDB Database Implementation

This module provides a DuckDB implementation of the DatabaseABC interface.
DuckDB is an embedded analytical database with SQL support.
"""
import duckdb
import os
from datetime import datetime
from typing import Type, Optional, List, Dict, Any
from .base import DatabaseABC


class DuckDBDatabase(DatabaseABC):
    """DuckDB 数据库实现

    提供 DuckDB 数据库的具体实现，包括：
    - 自动建表
    - CRUD 操作
    - 原生 SQL 执行
    - 外键约束
    """

    def __init__(self, db_path: str = "data/worklog.db"):
        """初始化 DuckDB 连接

        Args:
            db_path: 数据库文件路径，默认为 data/worklog.db
        """
        self.db_path = db_path
        self.conn: Optional[duckdb.DuckDBPyConnection] = None
        self._ensure_db_directory()

    def _ensure_db_directory(self) -> None:
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def connect(self) -> None:
        """连接数据库并初始化表结构"""
        self.conn = duckdb.connect(self.db_path)
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
        placeholders = ', '.join(['?' for _ in data])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING id"

        result = self.conn.execute(sql, list(data.values())).fetchone()
        return result[0] if result else None

    def get_by_id(self, model: Type, id: int) -> Optional[Any]:
        """根据 ID 获取数据"""
        table_name = model.__tablename__
        sql = f"SELECT * FROM {table_name} WHERE id = ?"
        result = self.conn.execute(sql, [id]).fetchone()
        return model(**dict(result)) if result else None

    def get_by_field(self, model: Type, field: str, value: Any) -> List[Any]:
        """根据字段获取数据列表"""
        table_name = model.__tablename__
        sql = f"SELECT * FROM {table_name} WHERE {field} = ?"
        results = self.conn.execute(sql, [value]).fetchall()
        return [model(**dict(row)) for row in results]

    def get_one_by_field(self, model: Type, field: str, value: Any) -> Optional[Any]:
        """根据字段获取单条数据"""
        results = self.get_by_field(model, field, value)
        return results[0] if results else None

    def update(self, model: Type, id: int, data: Dict[str, Any]) -> bool:
        """更新数据"""
        table_name = model.__tablename__
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
        self.conn.execute(sql, list(data.values()) + [id])
        return True

    def delete(self, model: Type, id: int) -> bool:
        """删除数据"""
        table_name = model.__tablename__
        sql = f"DELETE FROM {table_name} WHERE id = ?"
        self.conn.execute(sql, [id])
        return True

    def execute_sql(self, sql: str, params: Dict[str, Any] = None) -> List[Dict]:
        """执行原始 SQL"""
        result = self.conn.execute(sql, params or []).fetchall()
        return [dict(row) for row in result]

    def get_all(self, model: Type, limit: int = None, offset: int = 0) -> List[Any]:
        """获取所有数据"""
        table_name = model.__tablename__
        sql = f"SELECT * FROM {table_name}"
        if limit:
            sql += f" LIMIT {limit} OFFSET {offset}"
        results = self.conn.execute(sql).fetchall()
        return [model(**dict(row)) for row in results]

    def count(self, model: Type) -> int:
        """统计记录数"""
        table_name = model.__tablename__
        sql = f"SELECT COUNT(*) FROM {table_name}"
        result = self.conn.execute(sql).fetchone()
        return result[0] if result else 0

    def exists(self, model: Type, field: str, value: Any) -> bool:
        """检查记录是否存在"""
        table_name = model.__tablename__
        sql = f"SELECT COUNT(*) FROM {table_name} WHERE {field} = ?"
        result = self.conn.execute(sql, [value]).fetchone()
        return result[0] > 0 if result else False

    def _init_tables(self) -> None:
        """初始化表结构

        创建 users 和 user_configs 表，包含：
        - 主键约束
        - 外键约束
        - 唯一性约束
        - 默认值
        """
        # 创建 users 表
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建 user_configs 表
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_configs (
                id INTEGER PRIMARY KEY,
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
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_configs_user_id ON user_configs(user_id)
        """)

    def execute_sql_script(self, script: str) -> None:
        """执行 SQL 脚本（用于批量操作或迁移）"""
        self.conn.execute(script)

    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        sql = """
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = ?
        """
        result = self.conn.execute(sql, [table_name]).fetchone()
        return result[0] > 0 if result else False

    def get_table_info(self, table_name: str) -> List[Dict]:
        """获取表结构信息"""
        sql = f"DESCRIBE {table_name}"
        columns = self.conn.execute(sql).fetchall()
        return [dict(row) for row in columns]
