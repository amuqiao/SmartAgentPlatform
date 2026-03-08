from abc import ABC, abstractmethod
from typing import Any, Generator, Dict


class DatabaseConnection(ABC):
    """数据库连接基类"""

    @abstractmethod
    def connect(self) -> Any:
        """建立数据库连接"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """断开数据库连接"""
        pass

    @abstractmethod
    def get_session(self) -> Generator[Any, None, None]:
        """获取数据库会话"""
        pass
