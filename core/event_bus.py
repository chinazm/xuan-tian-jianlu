"""事件总线：发布/订阅模式，解耦系统间通信。"""
from typing import Callable
from collections import defaultdict


class EventBus:
    _subscribers: dict[str, list[Callable]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event_name: str, callback: Callable) -> None:
        """订阅事件。"""
        cls._subscribers[event_name].append(callback)

    @classmethod
    def unsubscribe(cls, event_name: str, callback: Callable) -> None:
        """取消订阅。"""
        if event_name in cls._subscribers:
            try:
                cls._subscribers[event_name].remove(callback)
            except ValueError:
                pass

    @classmethod
    def publish(cls, event_name: str, data: dict = None) -> None:
        """发布事件，通知所有订阅者。"""
        for cb in list(cls._subscribers.get(event_name, [])):
            cb(data or {})

    @classmethod
    def clear(cls) -> None:
        """清除所有订阅（用于测试）。"""
        cls._subscribers.clear()

    @classmethod
    def has_subscribers(cls, event_name: str) -> bool:
        """检查是否有订阅者。"""
        return len(cls._subscribers.get(event_name, [])) > 0


# --- 预定义事件常量 ---
# 这些是事件名称约定，供各系统参考使用。

ENTITY_EVENTS = [
    "entity_spawn",
    "entity_hit",
    "entity_die",
    "item_pickup",
]

PROGRESSION_EVENTS = [
    "stat_change",
    "level_up",
    "breakthrough_fail",
    "quest_start",
    "quest_complete",
    "objective_update",
]

GAME_EVENTS = [
    "room_enter",
    "room_exit",
    "dialogue_start",
    "dialogue_end",
    "game_pause",
    "game_save",
    "game_load",
]
