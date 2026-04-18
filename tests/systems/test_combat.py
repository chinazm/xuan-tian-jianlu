import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

from systems.combat import CombatSystem, Projectile
from entities.entity import Entity
from core.vector import Vector2


def test_spawn_projectile():
    cs = CombatSystem()
    proj = cs.spawn_projectile(Vector2(0, 0), Vector2(1, 0), 20, owner_id="player")
    assert len(cs.get_projectiles()) == 1
    assert proj.damage == 20
    assert proj.owner_id == "player"


def test_projectile_lifetime():
    cs = CombatSystem()
    cs.spawn_projectile(Vector2(0, 0), Vector2(1, 0), 20)
    for _ in range(200):
        cs.update(0.016, [])
    assert len(cs.get_projectiles()) == 0


def test_projectile_hits_target():
    cs = CombatSystem()
    target = Entity(entity_id="enemy", pos=Vector2(10, 0), size=Vector2(32, 32), max_hp=100, current_hp=100)
    cs.spawn_projectile(Vector2(0, 0), Vector2(1, 0), 30, owner_id="player")
    hits = cs.update(0.016, [target])
    assert len(hits) >= 1
    assert target.current_hp == 70


if __name__ == "__main__":
    test_spawn_projectile()
    test_projectile_lifetime()
    test_projectile_hits_target()
    print("All combat tests passed!")
