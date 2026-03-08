from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """用户基础模式"""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """用户创建模式"""
    password: str


class UserUpdate(BaseModel):
    """用户更新模式"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌响应模式"""
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """令牌数据模式"""
    user_id: Optional[int] = None
    username: Optional[str] = None
