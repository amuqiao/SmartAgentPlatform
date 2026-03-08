#!/usr/bin/env python3
"""独立测试DDD组件的脚本"""

import sys
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.insert(0, '/Users/wangqiao/Downloads/github_project/fastapi-enterprise-framework-template')

# 只导入DDD相关组件，不导入FastAPI应用
from src.domains.base.models.base import Base
from src.domains.user.models.user import User
from src.domains.user.schemas.user import UserCreate, UserUpdate
from src.domains.user.repositories.user_repository import UserRepositoryInterface
from src.infrastructure.repositories.sqlite.user_repository import SQLiteUserRepository
from src.domains.user.services.user_service import UserService


def test_ddd_components():
    """测试DDD组件"""
    print("🚀 开始测试DDD组件...")
    
    # 1. 创建临时SQLite数据库文件
    print("\n1. 创建临时SQLite数据库文件")
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db_path = temp_db.name
    temp_db.close()
    print(f"✅ 临时数据库文件创建成功: {temp_db_path}")
    
    # 2. 创建数据库引擎
    print("\n2. 创建数据库引擎")
    engine = create_engine(
        f"sqlite:///{temp_db_path}",
        connect_args={"check_same_thread": False}
    )
    print("✅ 数据库引擎创建成功")
    
    # 3. 创建会话工厂
    print("\n3. 创建会话工厂")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print("✅ 会话工厂创建成功")
    
    # 4. 创建所有表
    print("\n4. 创建所有表")
    Base.metadata.create_all(bind=engine)
    print("✅ 所有表创建成功")
    
    # 5. 获取数据库会话
    print("\n5. 获取数据库会话")
    session = SessionLocal()
    print("✅ 数据库会话获取成功")
    
    # 6. 测试用户仓储
    print("\n6. 测试用户仓储")
    user_repo = SQLiteUserRepository(session)
    
    # 6.1 测试创建用户
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": "hashed_password"
    }
    user = user_repo.create(user_data)
    print(f"✅ 用户创建成功: {user.username} ({user.email})")
    
    # 6.2 测试根据用户名获取用户
    fetched_user = user_repo.get_by_username("testuser")
    print(f"✅ 根据用户名获取用户成功: {fetched_user.username}")
    
    # 6.3 测试根据ID获取用户
    fetched_by_id = user_repo.get(user.id)
    print(f"✅ 根据ID获取用户成功: {fetched_by_id.username}")
    
    # 6.4 测试获取用户列表
    users = user_repo.get_multi()
    print(f"✅ 获取用户列表成功: {len(users)} 个用户")
    
    # 6.5 测试更新用户
    update_data = UserUpdate(username="updateduser")
    updated_user = user_repo.update(user.id, update_data)
    print(f"✅ 更新用户成功: {updated_user.username}")
    
    # 6.6 测试删除用户
    deleted_user = user_repo.delete(user.id)
    print(f"✅ 删除用户成功: {deleted_user.username}")
    
    # 6.7 验证用户已被删除
    assert user_repo.get(user.id) is None
    print("✅ 验证用户已被删除成功")
    
    # 7. 测试用户服务
    print("\n7. 测试用户服务")
    user_service = UserService(user_repo)
    
    # 7.1 测试用户注册
    test_user = UserCreate(
        username="testuser2",
        email="test2@example.com",
        password="testpassword123"
    )
    user = user_service.create_user(test_user)
    print(f"✅ 用户注册成功: {user['username']} ({user['email']})")
    
    # 7.2 测试用户认证
    authenticated_user = user_service.authenticate_user("testuser2", "testpassword123")
    print(f"✅ 用户认证成功: {authenticated_user['username']}")
    
    # 7.3 测试获取用户
    fetched_user = user_service.get_user_by_username("testuser2")
    print(f"✅ 获取用户成功: {fetched_user['username']}")
    
    # 7.4 测试生成令牌
    token = user_service.generate_token(authenticated_user)
    print(f"✅ 生成令牌成功: {token[:20]}...")
    
    # 8. 清理资源
    print("\n8. 清理资源")
    session.close()
    engine.dispose()
    os.unlink(temp_db_path)
    print("✅ 资源清理成功")
    
    print("\n🎉 所有DDD组件测试通过！")


if __name__ == "__main__":
    try:
        test_ddd_components()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
