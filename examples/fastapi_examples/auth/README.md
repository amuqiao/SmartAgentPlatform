# 认证示例

本示例展示如何使用FastAPI企业级框架模板的认证功能，包括JWT认证、OAuth2密码流等。

## 目录结构

```
examples/auth/
├── main.py              # 应用入口文件
├── models.py            # 用户数据模型
├── schemas.py           # Pydantic数据模型
├── dependencies.py      # 认证依赖
├── requirements.txt     # 依赖列表
└── README.md            # 本文件
```

## 功能说明

本示例实现了完整的用户认证系统，包含以下功能：
- 用户注册
- 用户登录（OAuth2密码流）
- JWT令牌验证
- 受保护的API端点
- 刷新令牌（可选）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python main.py
```

### 3. 测试认证流程

1. **用户注册**：使用POST请求到 `/api/v1/auth/register` 创建新用户
2. **用户登录**：使用POST请求到 `/api/v1/auth/login` 获取JWT令牌
3. **访问受保护资源**：使用获取到的JWT令牌作为Authorization头访问 `/api/v1/users/me`

## 示例代码

### main.py

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from app.config.settings import app_settings
from app.middleware import setup_cors
from app.dependencies.auth import get_current_user
from app.utils.password import get_password_hash, verify_password
from app.utils.jwt import create_access_token
from .models import User, Base
from .schemas import UserCreate, User as UserSchema, Token
from .dependencies import get_db

# 创建FastAPI应用
app = FastAPI(
    title=app_settings.APP_NAME,
    version=app_settings.APP_VERSION,
    openapi_url=f"{app_settings.API_V1_STR}/openapi.json",
)

# 设置CORS中间件
setup_cors(app)

# 初始化数据库
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=get_db().bind)

# 认证路由
@app.post(f"{app_settings.API_V1_STR}/auth/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post(f"{app_settings.API_V1_STR}/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}

# 用户路由
@app.get(f"{app_settings.API_V1_STR}/users/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@app.get(f"{app_settings.API_V1_STR}/users", response_model=List[UserSchema])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取用户列表"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# 根路径
@app.get("/")
def root():
    """根路径"""
    return {
        "message": "Welcome to FastAPI Enterprise Architecture - Auth Example",
        "version": app_settings.APP_VERSION,
        "api_v1": app_settings.API_V1_STR,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### models.py

```python
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
```

### schemas.py

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
```

### dependencies.py

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 创建SQLite数据库引擎
SQLALCHEMY_DATABASE_URL = "sqlite:///./auth_example.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 数据库依赖
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### requirements.txt

```
fastapi
uvicorn
pydantic
sqlalchemy
python-jose
passlib
python-multipart
```

## 核心概念说明

1. **OAuth2密码流**：使用FastAPI内置的OAuth2PasswordRequestForm处理用户名密码登录
2. **JWT认证**：使用JSON Web Token进行身份验证，包含过期时间和签名
3. **密码安全**：使用bcrypt算法对密码进行哈希处理，避免明文存储
4. **依赖注入**：使用FastAPI的依赖注入系统实现认证逻辑的复用
5. **受保护端点**：通过Depends(get_current_user)保护需要认证的API端点

## 下一步

- 查看[数据库示例](../database/README.md)：了解如何使用数据库抽象层
- 查看[事件示例](../events/README.md)：了解如何使用事件总线
- 查看[中间件示例](../middleware/README.md)：了解如何使用自定义中间件
