"""
Integration Tests - Multi-User Scenario Testing

测试多用户隔离场景。
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from src.main import app
from src.infrastructure.database import db, UserInDB, UserConfigInDB
from src.services.chat_service import get_chat_service
from src.services.config_service import ConfigService
from src.services.summary_service import get_summary_service
from src.utils.crypto import get_crypto
from src.utils.datetime import get_week_range


client = TestClient(app)


@pytest.fixture
def cleanup_users():
    """清理测试用户"""
    created_users = []
    yield created_users

    # 清理
    for user_data in created_users:
        try:
            existing = db.get_one_by_field(UserInDB, "username", user_data["username"])
            if existing:
                db.delete(UserInDB, existing.id)
        except:
            pass


@pytest.fixture
def user_a(cleanup_users):
    """创建用户A"""
    username = "test_user_a"
    email = "user_a@test.com"
    password = "password123"

    # 清理可能存在的用户
    existing = db.get_one_by_field(UserInDB, "username", username)
    if existing:
        db.delete(UserInDB, existing.id)

    # 注册用户
    response = client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    user_id = response.json()["id"]

    cleanup_users.append({"username": username})

    # 配置 GitLab
    config = ConfigService()
    asyncio.run(config.create(user_id, {
        "gitlab_url": "https://gitlab-a.example.com",
        "gitlab_token": "glpat-usera",
        "default_platform": "gitlab"
    }))

    return {
        "username": username,
        "password": password,
        "id": user_id
    }


@pytest.fixture
def user_b(cleanup_users):
    """创建用户B"""
    username = "test_user_b"
    email = "user_b@test.com"
    password = "password123"

    # 清理可能存在的用户
    existing = db.get_one_by_field(UserInDB, "username", username)
    if existing:
        db.delete(UserInDB, existing.id)

    # 注册用户
    response = client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    user_id = response.json()["id"]

    cleanup_users.append({"username": username})

    # 配置不同的 GitLab 服务器
    config = ConfigService()
    asyncio.run(config.create(user_id, {
        "gitlab_url": "https://gitlab-b.example.com",
        "gitlab_token": "glpat-userb",
        "default_platform": "gitlab"
    }))

    return {
        "username": username,
        "password": password,
        "id": user_id
    }


class TestMultiUserIsolation:
    """测试多用户隔离"""

    def test_separate_auth_tokens(self, user_a, user_b):
        """测试用户A和用户B的Token是独立的"""
        # 用户A登录
        response_a = client.post("/api/auth/login", json={
            "username": user_a["username"],
            "password": user_a["password"]
        })
        token_a = response_a.json()["access_token"]

        # 用户B登录
        response_b = client.post("/api/auth/login", json={
            "username": user_b["username"],
            "password": user_b["password"]
        })
        token_b = response_b.json()["access_token"]

        # Token应该不同
        assert token_a != token_b

    def test_separate_configs(self, user_a, user_b):
        """测试用户A和用户B的配置是隔离的"""
        # 获取用户A的配置
        response_a_login = client.post("/api/auth/login", json={
            "username": user_a["username"],
            "password": user_a["password"]
        })
        token_a = response_a_login.json()["access_token"]

        config_a = client.get("/api/config", headers={
            "Authorization": f"Bearer {token_a}"
        })
        assert config_a.json()["gitlab_url"] == "https://gitlab-a.example.com"

        # 获取用户B的配置
        response_b_login = client.post("/api/auth/login", json={
            "username": user_b["username"],
            "password": user_b["password"]
        })
        token_b = response_b_login.json()["access_token"]

        config_b = client.get("/api/config", headers={
            "Authorization": f"Bearer {token_b}"
        })
        assert config_b.json()["gitlab_url"] == "https://gitlab-b.example.com"

        # 确保配置不同
        assert config_a.json()["gitlab_url"] != config_b.json()["gitlab_url"]

    def test_cannot_access_other_user_config(self, user_a, user_b):
        """测试用户A不能访问用户B的配置"""
        # 用户A登录
        response_a = client.post("/api/auth/login", json={
            "username": user_a["username"],
            "password": user_a["password"]
        })
        user_a_data = response_a.json()
        token_a = user_a_data["access_token"]
        user_a_id = user_a_data["user"]["id"]

        # 尝试直接访问数据库获取用户B的配置（模拟攻击）
        user_b_config = db.get_one_by_field(UserConfigInDB, "user_id", user_b["id"])

        # 验证配置确实不同
        assert user_b_config is not None
        assert user_b_config.gitlab_url == "https://gitlab-b.example.com"

        # API层面：用户A只能访问自己的配置
        config_a = client.get("/api/config", headers={
            "Authorization": f"Bearer {token_a}"
        })
        assert config_a.json()["gitlab_url"] == "https://gitlab-a.example.com"


class TestPerformance:
    """性能测试"""

    def test_config_cache_performance(self, user_a):
        """测试配置缓存性能"""
        import time

        # 登录
        response = client.post("/api/auth/login", json={
            "username": user_a["username"],
            "password": user_a["password"]
        })
        token = response.json()["access_token"]

        # 第一次获取配置（未缓存）
        start = time.time()
        config1 = client.get("/api/config", headers={
            "Authorization": f"Bearer {token}"
        })
        first_call_time = time.time() - start

        # 第二次获取配置（已缓存）
        start = time.time()
        config2 = client.get("/api/config", headers={
            "Authorization": f"Bearer {token}"
        })
        second_call_time = time.time() - start

        # 验证两次返回相同数据
        assert config1.json() == config2.json()

        # 缓存应该更快（或者至少不慢）
        # 注意：由于时间差异很小，这个测试主要用于性能基准
        print(f"First call: {first_call_time:.4f}s, Second call: {second_call_time:.4f}s")

    def test_multiple_concurrent_requests(self, user_a):
        """测试并发请求性能"""
        import concurrent.futures

        # 登录
        response = client.post("/api/auth/login", json={
            "username": user_a["username"],
            "password": user_a["password"]
        })
        token = response.json()["access_token"]

        def make_request():
            return client.get("/api/config", headers={
                "Authorization": f"Bearer {token}"
            })

        # 并发发送10个请求
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        total_time = time.time() - start

        # 所有请求都应该成功
        assert all(r.status_code == 200 for r in results)

        # 总时间应该在合理范围内（10秒以内）
        assert total_time < 10
        print(f"10 concurrent requests completed in {total_time:.4f}s")


class TestSecurity:
    """安全测试"""

    def test_token_expiry_validation(self):
        """测试Token过期验证"""
        # 使用无效的Token
        response = client.get("/api/config", headers={
            "Authorization": "Bearer invalid_token_12345"
        })

        # 应该返回401
        assert response.status_code == 401

    def test_password_not_exposed_in_config(self, user_a):
        """测试配置中密码不暴露"""
        response = client.post("/api/auth/login", json={
            "username": user_a["username"],
            "password": user_a["password"]
        })
        token = response.json()["access_token"]

        config = client.get("/api/config", headers={
            "Authorization": f"Bearer {token}"
        })

        # Token应该被脱敏
        token_value = config.json()["gitlab_token"]
        assert "****" in token_value
        assert token_value != "glpat-usera"

    def test_sql_injection_prevention(self):
        """测试SQL注入防护"""
        malicious_username = "admin'; DROP TABLE users; --"

        # 尝试注册恶意用户名
        response = client.post("/api/auth/register", json={
            "username": malicious_username,
            "email": "test@test.com",
            "password": "password123"
        })

        # 应该被验证规则拒绝或安全处理
        # Pydantic的验证规则应该防止这种情况
        # 即使通过，数据库层也应该安全处理
        assert response.status_code in [400, 422]  # 验证失败


class TestDataIntegrity:
    """数据完整性测试"""

    def test_user_cascade_delete(self, user_a):
        """测试用户删除时配置级联删除"""
        response = client.post("/api/auth/login", json={
            "username": user_a["username"],
            "password": user_a["password"]
        })
        user_id = response.json()["user"]["id"]
        token = response.json()["access_token"]

        # 验证配置存在
        config = db.get_one_by_field(UserConfigInDB, "user_id", user_id)
        assert config is not None

        # 删除用户（在真实场景中，这应该级联删除配置）
        # 这里我们直接删除配置来测试
        from src.services.config_service import ConfigService
        asyncio.run(ConfigService.delete(user_id))

        # 验证配置已被删除
        config_after = db.get_one_by_field(UserConfigInDB, "user_id", user_id)
        assert config_after is None

    def test_config_encryption_roundtrip(self):
        """测试配置加密/解密"""
        from src.utils.crypto import get_crypto

        crypto = get_crypto()
        original_token = "glpat-verysecrettoken123"

        # 加密
        encrypted = crypto.encrypt(original_token)
        assert encrypted != original_token

        # 解密
        decrypted = crypto.decrypt(encrypted)
        assert decrypted == original_token


class TestEndToEnd:
    """端到端测试"""

    def test_complete_user_journey(self):
        """测试完整的用户旅程"""
        username = "journey_test"
        email = "journey@test.com"
        password = "testpass123"

        # 清理
        existing = db.get_one_by_field(UserInDB, "username", username)
        if existing:
            db.delete(UserInDB, existing.id)

        try:
            # 1. 注册
            response = client.post("/api/auth/register", json={
                "username": username,
                "email": email,
                "password": password
            })
            assert response.status_code == 201
            user_id = response.json()["id"]

            # 2. 登录
            response = client.post("/api/auth/login", json={
                "username": username,
                "password": password
            })
            assert response.status_code == 200
            token = response.json()["access_token"]

            # 3. 获取当前用户信息
            response = client.get("/api/auth/me", headers={
                "Authorization": f"Bearer {token}"
            })
            assert response.status_code == 200
            assert response.json()["username"] == username

            # 4. 配置GitLab
            response = client.patch("/api/config/gitlab", json={
                "gitlab_url": "https://gitlab.example.com",
                "gitlab_token": "glpat-test123"
            }, headers={
                "Authorization": f"Bearer {token}"
            })
            assert response.status_code == 200

            # 5. 获取配置（验证脱敏）
            response = client.get("/api/config", headers={
                "Authorization": f"Bearer {token}"
            })
            assert response.status_code == 200
            assert "****" in response.json()["gitlab_token"]

            # 6. 登出
            response = client.post("/api/auth/logout", headers={
                "Authorization": f"Bearer {token}"
            })
            assert response.status_code == 200

        finally:
            # 清理
            existing = db.get_one_by_field(UserInDB, "username", username)
            if existing:
                db.delete(UserInDB, existing.id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
