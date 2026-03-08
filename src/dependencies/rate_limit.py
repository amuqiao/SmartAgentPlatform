from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status

# 创建限流器实例，使用IP地址作为限流键
limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """限流异常处理器
    
    Args:
        request: 请求对象
        exc: 限流异常对象
    
    Returns:
        HTTPException: 包含限流信息的HTTP异常
    """
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=f"Rate limit exceeded: {exc.detail}",
        headers={
            "Retry-After": str(60),  # 默认重试时间为60秒
            "X-RateLimit-Limit": str(getattr(exc, 'limit', '100')),
            "X-RateLimit-Remaining": str(getattr(exc, 'remaining', '0')),
        },
    )
