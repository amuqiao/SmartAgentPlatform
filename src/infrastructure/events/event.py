from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime
from enum import Enum


class EventType(Enum):
    """事件类型枚举"""
    USER_REGISTERED = "user_registered"
    USER_LOGGED_IN = "user_logged_in"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"


class Event(ABC):
    """事件基类"""
    
    def __init__(self, event_type: EventType, data: Dict[str, Any] = None):
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = datetime.now()
        self.event_id = f"{event_type.value}-{self.timestamp.timestamp():.0f}"
    
    def to_dict(self) -> Dict[str, Any]:
        """将事件转换为字典格式"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }


class UserRegisteredEvent(Event):
    """用户注册事件"""
    
    def __init__(self, user_id: int, username: str, email: str):
        super().__init__(
            event_type=EventType.USER_REGISTERED,
            data={
                "user_id": user_id,
                "username": username,
                "email": email
            }
        )


class UserLoggedInEvent(Event):
    """用户登录事件"""
    
    def __init__(self, user_id: int, username: str, ip_address: str):
        super().__init__(
            event_type=EventType.USER_LOGGED_IN,
            data={
                "user_id": user_id,
                "username": username,
                "ip_address": ip_address
            }
        )
