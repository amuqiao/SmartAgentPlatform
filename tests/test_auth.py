import pytest
from fastapi.testclient import TestClient
from main import app
from src.domains.base.models.base import Base
from src.infrastructure.database.sqlite.connection import sqlite_connection

client = TestClient(app)


@pytest.fixture
def test_db():
    """测试数据库会话"""
    # 创建测试数据库表
    sqlite_connection.connect()
    Base.metadata.create_all(bind=sqlite_connection.engine)
    
    yield
    
    # 清理测试数据
    Base.metadata.drop_all(bind=sqlite_connection.engine)
    sqlite_connection.disconnect()


class TestUserAuth:
    """用户认证测试"""
    
    def test_user_register(self, test_db):
        """测试用户注册功能"""
        # 准备测试数据
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        # 发送注册请求
        response = client.post("/api/v1/auth/register", json=test_user)
        
        # 验证响应
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["email"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_user_login(self, test_db):
        """测试用户登录功能"""
        # 先注册一个测试用户
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        client.post("/api/v1/auth/register", json=test_user)
        
        # 测试登录（使用OAuth2表单格式）
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_get_user(self, test_db):
        """测试获取用户信息功能"""
        # 先注册一个测试用户
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        register_response = client.post("/api/v1/auth/register", json=test_user)
        user_id = register_response.json()["id"]
        
        # 测试获取用户信息
        response = client.get(f"/api/v1/users/{user_id}")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["email"]
    
    def test_invalid_login(self, test_db):
        """测试无效登录"""
        # 先注册一个测试用户
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        client.post("/api/v1/auth/register", json=test_user)
        
        # 测试使用错误密码登录
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        # 验证响应
        assert response.status_code == 401  # 预期认证失败
