from fastapi import Depends
from src.infrastructure.database.base import DatabaseConnection
from src.infrastructure.database.sqlite.connection import SQLiteConnection


class DatabaseManager:
    """数据库管理器，管理多个数据库连接"""

    def __init__(self):
        self._connections = {}

    def register(self, name: str, connection: DatabaseConnection) -> None:
        """注册数据库连接"""
        self._connections[name] = connection

    def get(self, name: str) -> DatabaseConnection:
        """获取数据库连接"""
        if name not in self._connections:
            raise ValueError(f"Database connection '{name}' not registered")
        return self._connections[name]

    def connect_all(self) -> None:
        """连接所有数据库"""
        for name, connection in self._connections.items():
            connection.connect()

    def disconnect_all(self) -> None:
        """断开所有数据库连接"""
        for name, connection in self._connections.items():
            connection.disconnect()


# 全局数据库管理器实例
database_manager = DatabaseManager()
# 创建SQLite连接实例并注册
sqlite_connection = SQLiteConnection()
database_manager.register("sqlite", sqlite_connection)


# 依赖注入函数 - 用于FastAPI Depends
def get_sqlite_db():
    """SQLite数据库会话依赖注入"""
    yield from sqlite_connection.get_session()


# 依赖注入容器 - 用于FastAPI Depends
class DatabaseDeps:
    """数据库依赖注入容器，提供统一的依赖注入接口"""

    @staticmethod
    def sqlite():
        return Depends(get_sqlite_db)


# 导出数据库依赖
db_deps = DatabaseDeps()
