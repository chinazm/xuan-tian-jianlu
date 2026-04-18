import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pygame
from systems.collision import CollisionSystem
from entities.entity import Entity
from core.vector import Vector2


def test_terrain_collision():
    cs = CollisionSystem()
    cs.set_terrain([pygame.Rect(100, 100, 100, 100)])
    assert not cs.check_terrain_collision(pygame.Rect(0, 0, 32, 32))
    assert cs.check_terrain_collision(pygame.Rect(110, 110, 32, 32))


def test_entity_collision():
    cs = CollisionSystem()
    a = Entity(entity_id="a", pos=Vector2(0, 0), size=Vector2(32, 32))
    b = Entity(entity_id="b", pos=Vector2(20, 20), size=Vector2(32, 32))
    assert cs.check_entity_collision(a, b)
    b.pos = Vector2(100, 100)
    assert not cs.check_entity_collision(a, b)


def test_nearby_entities():
    cs = CollisionSystem()
    e1 = Entity(entity_id="e1", pos=Vector2(0, 0))
    e2 = Entity(entity_id="e2", pos=Vector2(50, 0))
    e3 = Entity(entity_id="e3", pos=Vector2(200, 0))
    for e in [e1, e2, e3]:
        cs.add_entity(e)
    nearby = cs.get_nearby_entities(Vector2(0, 0), radius=100)
    assert len(nearby) == 2


def test_entities_in_rect():
    cs = CollisionSystem()
    e1 = Entity(entity_id="e1", pos=Vector2(10, 10), size=Vector2(32, 32))
    e2 = Entity(entity_id="e2", pos=Vector2(500, 500), size=Vector2(32, 32))
    cs.add_entity(e1)
    cs.add_entity(e2)
    in_rect = cs.get_entities_in_rect(pygame.Rect(0, 0, 100, 100))
    assert len(in_rect) == 1
    assert in_rect[0].entity_id == "e1"


if __name__ == "__main__":
    test_terrain_collision()
    test_entity_collision()
    test_nearby_entities()
    test_entities_in_rect()
    print("All collision tests passed!")
