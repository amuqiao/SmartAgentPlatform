#!/usr/bin/env python3
"""测试DDD组件的独立测试文件，不依赖FastAPI应用"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 只导入DDD相关组件，不导入FastAPI应用
from src.domains.base.models.base import Base
from src.domains.user.models.user import User
from src.domains.user.schemas.user import UserCreate, UserUpdate
from src.domains.user.repositories.user_repository import UserRepositoryInterface
from src.infrastructure.repositories.sqlite.user_repository import SQLiteUserRepository
from src.domains.user.services.user_service import UserService
from src.exception import BusinessException, AuthException


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    # 创建内存SQLite数据库
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话工厂
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 创建会话
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_user_repository_crud(db):
    """测试用户仓储的CRUD操作"""
    # 创建仓储实例
    user_repo = SQLiteUserRepository(db)
    
    # 测试创建用户
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": "hashed_password"
    }
    user = user_repo.create(user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.id is not None
    
    # 测试根据用户名获取用户
    fetched_user = user_repo.get_by_username("testuser")
    assert fetched_user is not None
    assert fetched_user.id == user.id
    
    # 测试根据ID获取用户
    fetched_by_id = user_repo.get(user.id)
    assert fetched_by_id is not None
    assert fetched_by_id.username == "testuser"
    
    # 测试获取用户列表
    users = user_repo.get_multi()
    assert len(users) == 1
    
    # 测试更新用户
    update_data = UserUpdate(username="updateduser")
    updated_user = user_repo.update(user.id, update_data)
    assert updated_user is not None
    assert updated_user.username == "updateduser"
    
    # 测试删除用户
    deleted_user = user_repo.delete(user.id)
    assert deleted_user is not None
    assert deleted_user.id == user.id
    
    # 验证用户已被删除
    assert user_repo.get(user.id) is None


def test_user_service_create_user(db):
    """测试用户服务的创建用户功能"""
    # 创建仓储和服务实例
    user_repo = SQLiteUserRepository(db)
    user_service = UserService(user_repo)
    
    # 测试用户注册
    test_user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword123"
    )
    user = user_service.create_user(test_user)
    assert user["username"] == "testuser"
    assert user["email"] == "test@example.com"
    assert "id" in user


def test_user_service_duplicate_username(db):
    """测试用户服务的用户名重复检测"""
    # 创建仓储和服务实例
    user_repo = SQLiteUserRepository(db)
    user_service = UserService(user_repo)
    
    # 先创建一个用户
    test_user1 = UserCreate(
        username="duplicateuser",
        email="user1@example.com",
        password="password123"
    )
    user_service.create_user(test_user1)
    
    # 尝试创建相同用户名的用户
    test_user2 = UserCreate(
        username="duplicateuser",
        email="user2@example.com",
        password="password456"
    )
    
    with pytest.raises(BusinessException) as excinfo:
        user_service.create_user(test_user2)
    
    assert excinfo.value.message == "Username already registered"
    assert excinfo.value.code == 409


def test_user_service_duplicate_email(db):
    """测试用户服务的邮箱重复检测"""
    # 创建仓储和服务实例
    user_repo = SQLiteUserRepository(db)
    user_service = UserService(user_repo)
    
    # 先创建一个用户
    test_user1 = UserCreate(
        username="user1",
        email="duplicate@example.com",
        password="password123"
    )
    user_service.create_user(test_user1)
    
    # 尝试创建相同邮箱的用户
    test_user2 = UserCreate(
        username="user2",
        email="duplicate@example.com",
        password="password456"
    )
    
    with pytest.raises(BusinessException) as excinfo:
        user_service.create_user(test_user2)
    
    assert excinfo.value.message == "Email already registered"
    assert excinfo.value.code == 409


def test_user_service_authentication_success(db):
    """测试用户服务的认证成功情况"""
    # 创建仓储和服务实例
    user_repo = SQLiteUserRepository(db)
    user_service = UserService(user_repo)
    
    # 创建测试用户
    test_user = UserCreate(
        username="authuser",
        email="auth@example.com",
        password="authpassword123"
    )
    user_service.create_user(test_user)
    
    # 测试认证成功
    authenticated_user = user_service.authenticate_user("authuser", "authpassword123")
    assert authenticated_user is not None
    assert authenticated_user["username"] == "authuser"


def test_user_service_authentication_invalid_username(db):
    """测试用户服务的无效用户名认证"""
    # 创建仓储和服务实例
    user_repo = SQLiteUserRepository(db)
    user_service = UserService(user_repo)
    
    # 尝试使用不存在的用户名认证
    with pytest.raises(AuthException) as excinfo:
        user_service.authenticate_user("nonexistent", "password123")
    
    assert excinfo.value.message == "Incorrect username or password"
    assert excinfo.value.code == 401


def test_user_service_authentication_invalid_password(db):
    """测试用户服务的无效密码认证"""
    # 创建仓储和服务实例
    user_repo = SQLiteUserRepository(db)
    user_service = UserService(user_repo)
    
    # 创建测试用户
    test_user = UserCreate(
        username="authuser",
        email="auth@example.com",
        password="correctpassword"
    )
    user_service.create_user(test_user)
    
    # 尝试使用错误密码认证
    with pytest.raises(AuthException) as excinfo:
        user_service.authenticate_user("authuser", "wrongpassword")
    
    assert excinfo.value.message == "Incorrect username or password"
    assert excinfo.value.code == 401
