"""
Configuration Service Tests

测试配置服务功能。
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.infrastructure.database import db, UserInDB, UserConfigInDB
from src.services.config_service import ConfigService


client = TestClient(app)


@pytest.fixture
def authenticated_user():
    """创建并登录测试用户"""
    username = "config_test_user"
    email = "config_test@example.com"
    password = "testpassword123"

    # 清理可能存在的测试用户
    existing = db.get_one_by_field(UserInDB, "username", username)
    if existing:
        db.delete(UserInDB, existing.id)

    # 注册
    register_response = client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })

    # 登录
    login_response = client.post("/api/auth/login", json={
        "username": username,
        "password": password
    })

    token = login_response.json()["access_token"]
    user_id = register_response.json()["id"]

    yield {
        "username": username,
        "user_id": user_id,
        "token": token
    }

    # 清理
    existing = db.get_one_by_field(UserInDB, "username", username)
    if existing:
        db.delete(UserInDB, existing.id)


class TestConfigService:
    """测试配置服务"""

    def test_create_gitlab_config(self, authenticated_user):
        """测试创建 GitLab 配置"""
        config_data = {
            "gitlab_url": "https://gitlab.example.com",
            "gitlab_token": "glpat-testtoken123",
            "default_platform": "gitlab"
        }

        # 使用服务创建
        config = ConfigService.create(
            authenticated_user["user_id"],
            config_data
        )

        assert config is not None
        assert config.gitlab_url == "https://gitlab.example.com"
        assert config.gitlab_token == "glpat-testtoken123"

    def test_get_config_by_user_id(self, authenticated_user):
        """测试根据用户 ID 获取配置"""
        # 先创建配置
        config_data = {
            "gitlab_url": "https://gitlab.example.com",
            "gitlab_token": "glpat-testtoken123",
            "default_platform": "gitlab"
        }
        ConfigService.create(authenticated_user["user_id"], config_data)

        # 获取配置
        config = ConfigService.get_by_user_id(authenticated_user["user_id"])

        assert config is not None
        assert config.gitlab_url == "https://gitlab.example.com"

    def test_update_config(self, authenticated_user):
        """测试更新配置"""
        # 先创建配置
        config_data = {
            "gitlab_url": "https://gitlab.example.com",
            "gitlab_token": "glpat-testtoken123",
            "default_platform": "gitlab"
        }
        ConfigService.create(authenticated_user["user_id"], config_data)

        # 更新配置
        from src.infrastructure.database.models import UserConfigUpdate
        config_update = UserConfigUpdate(
            gitlab_url="https://newgitlab.example.com",
            include_branches=True
        )

        updated = ConfigService.update(authenticated_user["user_id"], config_update)

        assert updated.gitlab_url == "https://newgitlab.example.com"
        assert updated.include_branches is True


class TestConfigAPI:
    """测试配置 API 端点"""

    def test_get_config_not_found(self, authenticated_user):
        """测试获取不存在的配置"""
        response = client.get("/api/config", headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        })

        assert response.status_code == 404

    def test_update_gitlab_config(self, authenticated_user):
        """测试更新 GitLab 配置 API"""
        response = client.patch("/api/config/gitlab", json={
            "gitlab_url": "https://gitlab.example.com",
            "gitlab_token": "glpat-testtoken123"
        }, headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_update_github_config(self, authenticated_user):
        """测试更新 GitHub 配置 API"""
        response = client.patch("/api/config/github", json={
            "github_username": "testuser",
            "github_token": "ghp_testtoken123"
        }, headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_get_config_masked(self, authenticated_user):
        """测试配置中的敏感信息被脱敏"""
        # 先创建配置
        client.patch("/api/config/gitlab", json={
            "gitlab_url": "https://gitlab.example.com",
            "gitlab_token": "glpat-verylongtoken123"
        }, headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        })

        # 获取配置
        response = client.get("/api/config", headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        })

        assert response.status_code == 200
        data = response.json()
        # Token 应该被脱敏
        assert len(data["gitlab_token"]) < len("glpat-verylongtoken123")
        assert "****" in data["gitlab_token"]

    def test_delete_config(self, authenticated_user):
        """测试删除配置"""
        # 先创建配置
        client.patch("/api/config/gitlab", json={
            "gitlab_url": "https://gitlab.example.com",
            "gitlab_token": "glpat-testtoken123"
        }, headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        })

        # 删除配置
        response = client.delete("/api/config", headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        })

        assert response.status_code == 200

        # 确认配置已删除
        response = client.get("/api/config", headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        })
        assert response.status_code == 404
