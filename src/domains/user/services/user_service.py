from typing import Optional
from src.domains.user.repositories.user_repository import UserRepositoryInterface
from src.domains.user.schemas.user import UserCreate, UserUpdate
from src.utils.password import get_password_hash, verify_password
from src.utils.jwt import create_access_token
from src.config.logger import logger
from src.exception import BusinessException, AuthException, NotFoundException


class UserService:
    """用户服务"""

    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    def get_user(self, user_id: int) -> Optional[dict]:
        """根据ID获取用户"""
        user = self.user_repository.get(user_id)
        if user:
            return user.__dict__  # 简单处理，实际应使用模型转换
        return None

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """根据用户名获取用户"""
        user = self.user_repository.get_by_username(username)
        if user:
            return user.__dict__
        return None

    def create_user(self, user_in: UserCreate) -> dict:
        """创建用户"""
        # 检查用户名是否已存在
        existing_user = self.user_repository.get_by_username(user_in.username)
        if existing_user:
            logger.warning(f"User registration failed: username {user_in.username} already exists")
            raise BusinessException(message="Username already registered", code=409)

        # 检查邮箱是否已存在
        existing_email = self.user_repository.get_by_email(user_in.email)
        if existing_email:
            logger.warning(f"User registration failed: email {user_in.email} already exists")
            raise BusinessException(message="Email already registered", code=409)

        # 创建新用户
        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.model_dump(exclude={"password"})
        user_data["password_hash"] = hashed_password
        
        user = self.user_repository.create(user_data)
        logger.info(f"User registered successfully: {user_in.username}")
        return user.__dict__

    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """用户认证"""
        user = self.user_repository.get_by_username(username)
        if not user:
            logger.warning(f"Authentication failed: user {username} not found")
            raise AuthException(message="Incorrect username or password")

        if not verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: incorrect password for user {username}")
            raise AuthException(message="Incorrect username or password")

        logger.info(f"User authenticated successfully: {username}")
        return user.__dict__

    @staticmethod
    def generate_token(user: any, ip_address: str = "unknown") -> str:
        """生成JWT令牌"""
        access_token = create_access_token(
            data={"sub": str(user["id"]), "username": user["username"]}
        )
        logger.info(f"Generated access token for user: {user['username']}")
        return access_token