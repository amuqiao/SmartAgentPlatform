from abc import abstractmethod
from typing import Optional, List
from src.domains.base.repositories.base import BaseRepository


class UserRepositoryInterface(BaseRepository):
    """用户仓储接口，定义用户相关的抽象方法"""
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[any]:
        """根据用户名获取用户"""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[any]:
        """根据邮箱获取用户"""
        pass
    
    @abstractmethod
    def create(self, user_in: dict) -> any:
        """创建用户"""
        pass
    
    @abstractmethod
    def update(self, user_id: int, user_in: any) -> Optional[any]:
        """更新用户"""
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> Optional[any]:
        """删除用户"""
        pass
