# Database Factory
"""
根据配置创建数据库实例
"""
from config.settings import settings
from infrastructure.database.base import DatabaseABC
from infrastructure.database.sqlite_impl import SQLiteDatabase
from infrastructure.database.postgres_impl import PostgreSQLDatabase
from infrastructure.database.mysql_impl import MySQLDatabase


def get_database() -> DatabaseABC:
    """获取数据库实例（根据配置自动选择实现）

    Returns:
        DatabaseABC: 数据库实例

    Raises:
        ValueError: 不支持的数据库类型
    """
    impl = settings.DATABASE_IMPLEMENTATION.lower()

    if impl == "sqlite":
        return SQLiteDatabase(db_path=settings.SQLITE_PATH)

    elif impl == "postgresql":
        return PostgreSQLDatabase(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DATABASE,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD
        )

    elif impl == "mysql":
        return MySQLDatabase(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            database=settings.MYSQL_DATABASE,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD
        )

    else:
        raise ValueError(
            f"Unsupported database implementation: {impl}. "
            f"Supported: sqlite, postgresql, mysql"
        )


# 全局单例
db: DatabaseABC = get_database()
