from src.config.base import BaseSettings
from typing import List, Optional


class AppSettings(BaseSettings):
    """应用主配置"""

    # 应用基本信息
    APP_NAME: str = "FastAPI Enterprise"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "FastAPI企业级框架"

    # 运行环境
    ENVIRONMENT: str = "development"  # development, testing, production
    DEBUG: bool = True

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    API_V1_STR: str = "/api/v1"

    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # JWT配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 配置文件优先级
    model_config = BaseSettings.model_config.copy()
    model_config["env_prefix"] = "APP_"  # 应用配置的环境变量前缀


# 创建全局配置实例 - 应用启动时自动加载配置
app_settings = AppSettings()
