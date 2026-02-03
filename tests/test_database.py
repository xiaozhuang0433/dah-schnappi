"""
Database Infrastructure Tests

测试数据库抽象层和 DuckDB 实现。
"""
import pytest
import os
import tempfile
from pathlib import Path

from src.infrastructure.database import DatabaseABC, DuckDBDatabase
from src.infrastructure.database.models import UserInDB, UserConfigInDB


@pytest.fixture
def test_db_path():
    """创建临时测试数据库"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    # 清理
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def db(test_db_path):
    """创建测试数据库实例"""
    database = DuckDBDatabase(test_db_path)
    database.connect()
    yield database
    database.disconnect()


class TestDuckDBDatabase:
    """测试 DuckDB 数据库实现"""

    def test_connect(self, db):
        """测试数据库连接"""
        assert db.conn is not None
        assert db.table_exists("users")
        assert db.table_exists("user_configs")

    def test_insert_user(self, db):
        """测试插入用户"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password"
        }
        user_id = db.insert(UserInDB, user_data)
        assert user_id is not None
        assert user_id > 0

    def test_get_user_by_id(self, db):
        """测试根据 ID 获取用户"""
        user_data = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password_hash": "hashed_password"
        }
        user_id = db.insert(UserInDB, user_data)

        user = db.get_by_id(UserInDB, user_id)
        assert user is not None
        assert user.username == "testuser2"
        assert user.email == "test2@example.com"

    def test_get_user_by_field(self, db):
        """测试根据字段获取用户"""
        user_data = {
            "username": "testuser3",
            "email": "test3@example.com",
            "password_hash": "hashed_password"
        }
        db.insert(UserInDB, user_data)

        users = db.get_by_field(UserInDB, "username", "testuser3")
        assert len(users) == 1
        assert users[0].email == "test3@example.com"

    def test_get_one_by_field(self, db):
        """测试根据字段获取单个用户"""
        user_data = {
            "username": "testuser4",
            "email": "test4@example.com",
            "password_hash": "hashed_password"
        }
        db.insert(UserInDB, user_data)

        user = db.get_one_by_field(UserInDB, "username", "testuser4")
        assert user is not None
        assert user.email == "test4@example.com"

    def test_update_user(self, db):
        """测试更新用户"""
        user_data = {
            "username": "testuser5",
            "email": "test5@example.com",
            "password_hash": "hashed_password"
        }
        user_id = db.insert(UserInDB, user_data)

        success = db.update(UserInDB, user_id, {"email": "updated@example.com"})
        assert success is True

        user = db.get_by_id(UserInDB, user_id)
        assert user.email == "updated@example.com"

    def test_delete_user(self, db):
        """测试删除用户"""
        user_data = {
            "username": "testuser6",
            "email": "test6@example.com",
            "password_hash": "hashed_password"
        }
        user_id = db.insert(UserInDB, user_data)

        success = db.delete(UserInDB, user_id)
        assert success is True

        user = db.get_by_id(UserInDB, user_id)
        assert user is None

    def test_count_users(self, db):
        """测试统计用户数"""
        initial_count = db.count(UserInDB)

        db.insert(UserInDB, {
            "username": "testuser7",
            "email": "test7@example.com",
            "password_hash": "hashed_password"
        })

        assert db.count(UserInDB) == initial_count + 1

    def test_exists_user(self, db):
        """测试检查用户是否存在"""
        assert not db.exists(UserInDB, "username", "testuser8")

        db.insert(UserInDB, {
            "username": "testuser8",
            "email": "test8@example.com",
            "password_hash": "hashed_password"
        })

        assert db.exists(UserInDB, "username", "testuser8")

    def test_user_config(self, db):
        """测试用户配置操作"""
        # 先创建用户
        user_id = db.insert(UserInDB, {
            "username": "testuser9",
            "email": "test9@example.com",
            "password_hash": "hashed_password"
        })

        # 插入配置
        config_data = {
            "user_id": user_id,
            "gitlab_url": "https://gitlab.example.com",
            "gitlab_token": "encrypted_token",
            "default_platform": "gitlab"
        }
        config_id = db.insert(UserConfigInDB, config_data)
        assert config_id is not None

        # 查询配置
        config = db.get_one_by_field(UserConfigInDB, "user_id", user_id)
        assert config is not None
        assert config.gitlab_url == "https://gitlab.example.com"

        # 删除用户（级联删除配置）
        db.delete(UserInDB, user_id)
        config = db.get_one_by_field(UserConfigInDB, "user_id", user_id)
        assert config is None

    def test_execute_sql(self, db):
        """测试执行原始 SQL"""
        results = db.execute_sql("SELECT * FROM users")
        assert isinstance(results, list)

    def test_get_all_users(self, db):
        """测试获取所有用户"""
        # 插入测试数据
        for i in range(5):
            db.insert(UserInDB, {
                "username": f"bulkuser{i}",
                "email": f"bulk{i}@example.com",
                "password_hash": "hashed_password"
            })

        users = db.get_all(UserInDB, limit=3)
        assert len(users) >= 3

        users_with_offset = db.get_all(UserInDB, limit=2, offset=2)
        assert len(users_with_offset) >= 2


class TestDatabaseAbstraction:
    """测试数据库抽象层接口"""

    def test_database_abc_is_abstract(self):
        """测试抽象基类不能直接实例化"""
        with pytest.raises(TypeError):
            DatabaseABC()
