# FastAPI依赖注入模块
# 集中管理所有依赖注入，提供统一的导入入口

# 直接导入依赖注入函数，简化设计

# 配置依赖
from src.dependencies.config import (
    get_app_settings,
    get_sqlite_config,
    get_logging_config,
)

# 数据库依赖
from src.dependencies.database import (
    get_sqlite_db,
)

# 认证依赖
from src.dependencies.auth import (
    get_current_user,
    oauth2_scheme,
)

# 服务层依赖
from src.dependencies.service import (
    get_user_service,
)

# 导出所有依赖注入函数
__all__ = [
    # 配置依赖
    "get_app_settings",
    "get_sqlite_config",
    "get_logging_config",
    # 数据库依赖
    "get_sqlite_db",
    # 认证依赖
    "get_current_user",
    "oauth2_scheme",
    # 服务层依赖
    "get_user_service",
]

