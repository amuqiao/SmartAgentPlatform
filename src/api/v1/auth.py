from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from src.domains.user.schemas.user import UserCreate, UserResponse, Token
from src.config.settings import app_settings
from src.dependencies.service import get_user_service

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(
    user_create: UserCreate,
    user_service = Depends(get_user_service),
):
    """用户注册"""
    user = user_service.create_user(user_create)
    return user


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service = Depends(get_user_service),
):
    """用户登录"""
    # 获取客户端IP地址
    client_ip = request.client.host if request.client else "unknown"

    # 验证用户
    user = user_service.authenticate_user(form_data.username, form_data.password)

    # 生成访问令牌，传递IP地址
    access_token = user_service.generate_token(user, ip_address=client_ip)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": app_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
