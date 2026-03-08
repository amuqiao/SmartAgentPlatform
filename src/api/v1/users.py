from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from src.domains.user.schemas.user import UserCreate, UserResponse, Token
from src.domains.user.services.user_service import UserService
from src.dependencies.service import get_user_service
from src.dependencies.auth import get_current_user
from src.config.settings import app_settings

router = APIRouter()


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """用户注册"""
    user = user_service.create_user(user_in)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
def login_user(
    login_request: LoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    """用户登录"""
    user = user_service.authenticate_user(login_request.username, login_request.password)
    access_token = user_service.generate_token(user)
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
def get_current_user(
    current_user = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """根据ID获取用户"""
    return user_service.get_user(user_id)
