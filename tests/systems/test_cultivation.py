import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from systems.cultivation import CultivationSystem
from core.event_bus import EventBus


def test_cultivation_load():
    EventBus.clear()
    cs = CultivationSystem("data/realms.json")
    assert cs.current_realm_name == "炼气期"
    assert cs.realm_level == 1
    assert cs.lingli == 0.0


def test_add_lingli():
    EventBus.clear()
    cs = CultivationSystem("data/realms.json")
    cs.add_lingli(10)
    assert cs.lingli == 10.0


def test_progress():
    EventBus.clear()
    cs = CultivationSystem("data/realms.json")
    cs.lingli = 25
    assert abs(cs.get_progress() - 0.5) < 0.01


if __name__ == "__main__":
    test_cultivation_load()
    test_add_lingli()
    test_progress()
    print("All cultivation tests passed!")
