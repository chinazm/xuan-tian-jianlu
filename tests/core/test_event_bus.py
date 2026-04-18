"""事件总线单元测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.event_bus import EventBus


def test_subscribe_and_publish():
    EventBus.clear()
    results = []

    def handler(data):
        results.append(data)

    EventBus.subscribe("entity_hit", handler)
    EventBus.publish("entity_hit", {"damage": 10})

    assert len(results) == 1
    assert results[0]["damage"] == 10


def test_multiple_subscribers():
    EventBus.clear()
    results_a = []
    results_b = []

    EventBus.subscribe("level_up", lambda d: results_a.append(d))
    EventBus.subscribe("level_up", lambda d: results_b.append(d))

    EventBus.publish("level_up", {"level": 2})

    assert len(results_a) == 1
    assert len(results_b) == 1


def test_unsubscribe():
    EventBus.clear()
    results = []
    handler = lambda d: results.append(d)

    EventBus.subscribe("test", handler)
    EventBus.unsubscribe("test", handler)
    EventBus.publish("test", {})

    assert len(results) == 0


def test_unsubscribe_nonexistent():
    """取消不存在的订阅不应报错"""
    EventBus.clear()
    handler = lambda d: None
    EventBus.unsubscribe("nonexistent", handler)  # Should not raise


def test_no_subscribers_does_not_crash():
    EventBus.clear()
    EventBus.publish("nonexistent_event", {"data": 123})


def test_clear():
    EventBus.clear()
    count = [0]
    EventBus.subscribe("test", lambda d: count.__setitem__(0, count[0] + 1))
    EventBus.publish("test", {})
    assert count[0] == 1

    EventBus.clear()
    EventBus.publish("test", {})
    assert count[0] == 1  # 不应再增加


def test_has_subscribers():
    EventBus.clear()
    assert not EventBus.has_subscribers("test")
    EventBus.subscribe("test", lambda d: None)
    assert EventBus.has_subscribers("test")


def test_publish_with_none_data():
    """data=None 时应传空字典"""
    EventBus.clear()
    received = []
    EventBus.subscribe("test", lambda d: received.append(d))
    EventBus.publish("test")
    assert received[0] == {}


if __name__ == "__main__":
    test_subscribe_and_publish()
    test_multiple_subscribers()
    test_unsubscribe()
    test_unsubscribe_nonexistent()
    test_no_subscribers_does_not_crash()
    test_clear()
    test_has_subscribers()
    test_publish_with_none_data()
    print("All event bus tests passed!")
