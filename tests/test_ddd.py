#!/usr/bin/env python3
"""测试DDD组件的简单脚本"""

import sys
from sqlalchemy.orm import Session
from src.infrastructure.database.sqlite.connection import SQLiteConnection
from src.domains.base.models.base import Base
from src.domains.user.models.user import User
from src.domains.user.schemas.user import UserCreate
from src.domains.user.repositories.user_repository import UserRepositoryInterface
from src.infrastructure.repositories.sqlite.user_repository import SQLiteUserRepository
from src.domains.user.services.user_service import UserService


# 初始化SQLite连接
sqlite_conn = SQLiteConnection()
sqlite_conn.connect()

# 创建所有表
Base.metadata.create_all(bind=sqlite_conn.engine)

print("✅ 数据库连接和表创建成功")

# 获取数据库会话
session = next(sqlite_conn.get_session())

# 测试用户仓储
user_repo = SQLiteUserRepository(session)
print("✅ 用户仓储初始化成功")

# 测试用户服务
user_service = UserService(user_repo)
print("✅ 用户服务初始化成功")

# 测试用户注册
test_user = UserCreate(
    username="testuser",
    email="test@example.com",
    password="testpassword123"
)

# 先检查并删除已存在的测试用户，确保每次运行都从干净状态开始
existing_user = user_service.get_user_by_username(test_user.username)
if existing_user:
    user_repo.delete(existing_user['id'])
    print("⚠️  已删除存在的测试用户，准备重新注册")

user = user_service.create_user(test_user)
print(f"✅ 用户注册成功: {user['username']} ({user['email']})")

# 测试用户认证
authenticated_user = user_service.authenticate_user("testuser", "testpassword123")
print(f"✅ 用户认证成功: {authenticated_user['username']}")

# 测试获取用户
fetched_user = user_service.get_user_by_username("testuser")
print(f"✅ 获取用户成功: {fetched_user['username']}")

# 测试生成令牌
token = user_service.generate_token(authenticated_user)
print(f"✅ 生成令牌成功: {token[:20]}...")

# 清理资源
session.close()

# 删除所有表，确保下次运行从干净状态开始
Base.metadata.drop_all(bind=sqlite_conn.engine)

sqlite_conn.disconnect()

print("\n🎉 所有测试通过！DDD组件工作正常")
