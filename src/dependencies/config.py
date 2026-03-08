from fastapi import Depends
from src.config.base import BaseSettings
from src.config.settings import app_settings, AppSettings
from src.config.database import sqlite_config, SQLiteConfig
from src.config.logger import logging_config, LoggingConfig


# 配置依赖注入函数
def get_app_settings() -> AppSettings:
    """获取应用主配置"""
    return app_settings


def get_sqlite_config() -> SQLiteConfig:
    """获取SQLite配置"""
    return sqlite_config


def get_logging_config() -> LoggingConfig:
    """获取日志配置"""
    return logging_config


# 配置依赖注入容器
class ConfigDeps:
    """配置依赖注入容器，提供统一的配置访问接口"""

    @staticmethod
    def app():
        """应用主配置依赖"""
        return Depends(get_app_settings)

    @staticmethod
    def sqlite():
        """SQLite配置依赖"""
        return Depends(get_sqlite_config)

    @staticmethod
    def logging():
        """日志配置依赖"""
        return Depends(get_logging_config)


# 创建依赖容器实例
config_deps = ConfigDeps()
