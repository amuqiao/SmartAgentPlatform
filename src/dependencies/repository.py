from fastapi import Depends
from src.dependencies.database import get_sqlite_db
from src.infrastructure.repositories.sqlite.user_repository import SQLiteUserRepository
from src.domains.user.repositories.user_repository import UserRepositoryInterface


# 依赖注入函数
def get_sqlite_user_repository(db = Depends(get_sqlite_db)):
    """SQLite用户仓储依赖注入"""
    return SQLiteUserRepository(db)

# 导出仓储依赖，供服务层使用
export_repo_deps = {
    "user_repository": get_sqlite_user_repository
}
