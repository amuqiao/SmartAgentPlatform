from abc import ABC, abstractmethod
from typing import Optional, List


class BaseRepository(ABC):
    """仓储基类接口，定义仓储层通用接口"""

    @abstractmethod
    def get(self, id: int):
        """根据ID获取实体"""
        pass

    @abstractmethod
    def get_multi(self, skip: int = 0, limit: int = 100):
        """获取实体列表"""
        pass
