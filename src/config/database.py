from src.config.base import BaseSettings
from typing import Optional


class SQLiteConfig(BaseSettings):
    """SQLite数据库配置"""

    HOST: Optional[str] = None  # SQLite不需要host，但保留字段以保持一致性
    PORT: Optional[int] = None  # SQLite不需要port，但保留字段以保持一致性
    USER: Optional[str] = None  # SQLite不需要user，但保留字段以保持一致性
    PASSWORD: Optional[str] = None  # SQLite不需要password，但保留字段以保持一致性
    DATABASE: str = "fastapi_enterprise"
    DATABASE_FILE: str = "app.db"

    # SQLAlchemy配置
    ECHO_SQL: bool = False

    @property
    def URL(self) -> str:
        """生成SQLite连接URL"""
        return f"sqlite:///{self.DATABASE_FILE}"

    model_config = BaseSettings.model_config.copy()
    model_config["env_prefix"] = "SQLITE_"


# 创建数据库配置实例
sqlite_config = SQLiteConfig()