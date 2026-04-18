import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

from entities.entity import Entity
from core.vector import Vector2
from core.event_bus import EventBus


def test_entity_creation():
    e = Entity(entity_id="test_001", pos=Vector2(100, 200))
    assert e.entity_id == "test_001"
    assert e.pos.x == 100
    assert e.is_alive


def test_take_damage():
    EventBus.clear()
    e = Entity(entity_id="test", pos=Vector2(0, 0), max_hp=100, current_hp=100)
    e.take_damage(30, Vector2(0, 50))
    assert e.current_hp == 70
    assert e.is_knockback


def test_death():
    EventBus.clear()
    e = Entity(entity_id="test", pos=Vector2(0, 0), max_hp=50, current_hp=50)
    e.take_damage(50, Vector2(0, 50))
    assert e.current_hp == 0
    assert not e.is_alive


def test_heal():
    e = Entity(entity_id="test", pos=Vector2(0, 0), max_hp=100, current_hp=50)
    e.heal(30)
    assert e.current_hp == 80
    e.heal(50)
    assert e.current_hp == 100


def test_collision_rect():
    e = Entity(entity_id="test", pos=Vector2(100, 200), size=Vector2(32, 32))
    rect = e.get_collision_rect()
    assert rect.x == 100 and rect.y == 200 and rect.width == 32 and rect.height == 32


if __name__ == "__main__":
    test_entity_creation()
    test_take_damage()
    test_death()
    test_heal()
    test_collision_rect()
    print("All entity tests passed!")
