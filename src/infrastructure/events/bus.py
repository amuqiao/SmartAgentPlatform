from typing import Any, Dict, Callable, Union, List
from asyncio import Queue, create_task, gather
import asyncio
import logging
from .event import Event, EventType

# 配置日志
logger = logging.getLogger("app.infrastructure.events")


class EventBus:
    """事件总线，用于发布和订阅事件"""
    
    def __init__(self):
        # 事件队列，用于异步处理事件
        self.event_queue = Queue()
        # 事件订阅者字典，key为事件类型，value为订阅者列表
        # 每个订阅者是一个元组：(handler, is_async)
        self.subscribers = {}
        # 事件处理器任务列表
        self.event_tasks = []
        # 事件处理是否已启动
        self.running = False
    
    def subscribe(self, event_type: EventType, handler: Union[Callable[[Event], None], Callable[[Event], asyncio.Future]]):
        """订阅事件，支持同步和异步处理器"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        # 检查处理器是否为异步函数
        is_async = asyncio.iscoroutinefunction(handler)
        self.subscribers[event_type].append((handler, is_async))
    
    def unsubscribe(self, event_type: EventType, handler: Union[Callable[[Event], None], Callable[[Event], asyncio.Future]]):
        """取消订阅事件"""
        if event_type in self.subscribers:
            self.subscribers[event_type] = [(h, is_async) for h, is_async in self.subscribers[event_type] if h != handler]
    
    def publish(self, event: Event):
        """发布事件"""
        # 将事件放入队列
        self.event_queue.put_nowait(event)
        logger.info(f"Published event: {event.to_dict()}")
        # 立即通知所有订阅者
        self._notify_subscribers(event)
    
    def _notify_subscribers(self, event: Event):
        """通知所有订阅者"""
        if event.event_type in self.subscribers:
            for handler, is_async in self.subscribers[event.event_type]:
                try:
                    if is_async:
                        # 异步处理器，使用事件循环执行
                        create_task(handler(event))
                    else:
                        # 同步处理器，直接执行
                        handler(event)
                except Exception as e:
                    logger.error(f"Error handling event {event.event_type}: {e}", exc_info=True)
    
    def start(self):
        """启动事件处理"""
        if not self.running:
            self.running = True
            # 创建事件处理任务
            task = create_task(self.process_events())
            self.event_tasks.append(task)
            logger.info("Event bus started")
    
    def stop(self):
        """停止事件处理"""
        self.running = False
        # 取消所有事件处理任务
        for task in self.event_tasks:
            task.cancel()
        self.event_tasks.clear()
        logger.info("Event bus stopped")
    
    async def process_events(self):
        """异步处理事件队列"""
        while self.running:
            try:
                # 从队列中获取事件，设置超时，以便定期检查running状态
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                try:
                    # 这里可以添加更多的异步事件处理逻辑
                    logger.debug(f"Asynchronously processed event: {event.event_id}")
                finally:
                    # 标记事件为已处理
                    self.event_queue.task_done()
            except asyncio.TimeoutError:
                # 超时，继续循环检查running状态
                continue
            except asyncio.CancelledError:
                # 任务被取消
                break
            except Exception as e:
                logger.error(f"Error in event processing loop: {e}", exc_info=True)
    
    async def flush_events(self):
        """等待所有事件处理完成"""
        await self.event_queue.join()


# 创建全局事件总线实例
event_bus = EventBus()
