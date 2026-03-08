import pytest
from src.dependencies.database import database_manager, sqlite_connection


def test_database_manager_registration():
    """测试数据库管理器注册功能"""
    # 检查SQLite连接是否已注册
    assert database_manager._connections.get("sqlite") is not None
    assert database_manager.get("sqlite") == sqlite_connection


def test_database_connect_disconnect():
    """测试数据库连接和断开功能"""
    # 连接数据库
    database_manager.connect_all()
    # 检查连接是否成功
    assert sqlite_connection._engine is not None

    # 断开数据库
    database_manager.disconnect_all()
    # 检查连接是否断开
    assert sqlite_connection._engine is None
