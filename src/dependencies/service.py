from fastapi import Depends
from src.domains.user.services.user_service import UserService
from src.dependencies.repository import get_sqlite_user_repository


# 服务层依赖注入函数
def get_user_service(user_repository = Depends(get_sqlite_user_repository)):
    """用户服务依赖注入"""
    return UserService(user_repository)


# 服务层依赖容器
class ServiceDeps:
    """服务层依赖注入容器"""
    
    @staticmethod
    def user_service():
        return Depends(get_user_service)


# 导出服务依赖
service_deps = ServiceDeps()
