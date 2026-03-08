from fastapi import APIRouter, Depends, Security, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.dependencies.database import get_sqlite_db
from src.dependencies.rate_limit import limiter
from src.dependencies.auth import auth_deps
from src.config.logger import logger

# 创建健康检查路由
router = APIRouter()


@router.get("/liveness", summary="服务存活检查", tags=["健康检查"])
@limiter.limit("100/minute")
def liveness_check(request: Request):
    """服务存活检查接口
    
    用于检查服务是否正在运行，不依赖任何外部服务
    
    Args:
        request: 请求对象，用于限流
    
    Returns:
        dict: 包含服务状态的响应
    """
    logger.info("Liveness check called")
    return {
        "status": "ok",
        "message": "Service is running",
    }


@router.get("/readiness", summary="服务就绪检查", tags=["健康检查"])
@limiter.limit("100/minute")
def readiness_check(request: Request, db: Session = Depends(get_sqlite_db)):
    """服务就绪检查接口
    
    用于检查服务是否准备就绪，包括数据库连接检查
    
    Args:
        request: 请求对象，用于限流
        db: 数据库会话依赖
    
    Returns:
        dict: 包含服务状态和检查结果的响应
    """
    logger.info("Readiness check called")
    
    # 检查数据库连接
    try:
        # 执行简单的SQL查询来测试数据库连接
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        db_status = "error"
    
    # 综合判断服务是否就绪
    overall_status = "ok" if db_status == "ok" else "error"
    
    return {
        "status": overall_status,
        "message": "Service readiness check",
        "checks": {
            "database": db_status,
        },
    }
