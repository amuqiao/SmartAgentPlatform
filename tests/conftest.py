import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# 创建测试数据库引擎
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建测试会话工厂
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    # 只导入DDD相关组件
    from src.domains.base.models.base import Base
    from src.domains.user.models.user import User

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 测试结束后删除所有表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(db):
    """创建测试用户"""
    from src.domains.user.models.user import User
    from src.utils.password import get_password_hash

    # 创建测试用户
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture(scope="function")
def client(db):
    """创建FastAPI测试客户端"""
    from main import app
    from src.dependencies.database import get_sqlite_db
    
    # 重写get_sqlite_db依赖，返回测试数据库会话
    def override_get_sqlite_db():
        try:
            yield db
        finally:
            pass  # 数据库会话由db fixture管理
    
    # 重写应用的依赖
    app.dependency_overrides[get_sqlite_db] = override_get_sqlite_db
    
    # 创建测试客户端
    with TestClient(app) as client:
        yield client
    
    # 恢复原始依赖
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user_token(client, test_user):
    """创建测试用户令牌"""
    from src.utils.jwt import create_access_token
    
    # 创建JWT令牌
    access_token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username}
    )
    
    return access_token
