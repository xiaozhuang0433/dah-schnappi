"""
Authentication Tests

测试认证模块功能。
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.infrastructure.database import db, UserInDB
from src.auth.security import get_password_hash, create_access_token, decode_access_token


client = TestClient(app)


@pytest.fixture
def test_user():
    """创建测试用户"""
    username = "testuser_auth"
    email = "test_auth@example.com"
    password = "testpassword123"

    # 清理可能存在的测试用户
    existing = db.get_one_by_field(UserInDB, "username", username)
    if existing:
        db.delete(UserInDB, existing.id)

    yield {
        "username": username,
        "email": email,
        "password": password
    }

    # 清理
    existing = db.get_one_by_field(UserInDB, "username", username)
    if existing:
        db.delete(UserInDB, existing.id)


class TestPasswordSecurity:
    """测试密码安全功能"""

    def test_password_hashing(self):
        """测试密码哈希"""
        password = "mypassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 50  # bcrypt 哈希长度

    def test_password_verification(self):
        """测试密码验证"""
        password = "mypassword123"
        hashed = get_password_hash(password)

        from src.auth.security import verify_password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False


class TestJWTToken:
    """测试 JWT Token 功能"""

    def test_create_token(self):
        """测试创建 Token"""
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100

    def test_decode_token(self):
        """测试解码 Token"""
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"

    def test_invalid_token(self):
        """测试无效 Token"""
        payload = decode_access_token("invalid_token")
        assert payload is None


class TestAuthEndpoints:
    """测试认证端点"""

    def test_register_user(self, test_user):
        """测试用户注册"""
        response = client.post("/api/auth/register", json={
            "username": test_user["username"],
            "email": test_user["email"],
            "password": test_user["password"]
        })

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["email"]
        assert "id" in data
        assert "password" not in data

    def test_register_duplicate_username(self, test_user):
        """测试重复用户名注册"""
        # 第一次注册
        client.post("/api/auth/register", json={
            "username": test_user["username"],
            "email": test_user["email"],
            "password": test_user["password"]
        })

        # 第二次注册（应该失败）
        response = client.post("/api/auth/register", json={
            "username": test_user["username"],
            "email": "different@example.com",
            "password": "password123"
        })

        assert response.status_code == 400

    def test_login_success(self, test_user):
        """测试成功登录"""
        # 先注册
        client.post("/api/auth/register", json={
            "username": test_user["username"],
            "email": test_user["email"],
            "password": test_user["password"]
        })

        # 登录
        response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_login_wrong_password(self, test_user):
        """测试错误密码登录"""
        # 先注册
        client.post("/api/auth/register", json={
            "username": test_user["username"],
            "email": test_user["email"],
            "password": test_user["password"]
        })

        # 错误密码登录
        response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": "wrongpassword"
        })

        assert response.status_code == 401

    def test_get_current_user(self, test_user):
        """测试获取当前用户信息"""
        # 注册并登录
        client.post("/api/auth/register", json={
            "username": test_user["username"],
            "email": test_user["email"],
            "password": test_user["password"]
        })

        login_response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        token = login_response.json()["access_token"]

        # 获取当前用户
        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["email"]

    def test_get_current_user_without_token(self):
        """测试无 Token 访问受保护端点"""
        response = client.get("/api/auth/me")

        assert response.status_code == 403  # 没有 Bearer token

    def test_logout(self, test_user):
        """测试登出"""
        # 注册并登录
        client.post("/api/auth/register", json={
            "username": test_user["username"],
            "email": test_user["email"],
            "password": test_user["password"]
        })

        login_response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        token = login_response.json()["access_token"]

        # 登出
        response = client.post("/api/auth/logout", headers={
            "Authorization": f"Bearer {token}"
        })

        assert response.status_code == 200
