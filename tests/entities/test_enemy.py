import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

from entities.enemy import Enemy
from core.vector import Vector2


def test_enemy_patrol():
    e = Enemy(entity_id="slime_1", pos=Vector2(100, 100), patrol_center=Vector2(100, 100), patrol_radius=50)
    assert e.state == "patrol"
    e.update(0.016)
    assert e.is_alive


def test_enemy_can_see():
    e = Enemy(entity_id="slime_1", pos=Vector2(0, 0))
    assert e.can_see_player(Vector2(100, 0), max_distance=200)
    assert not e.can_see_player(Vector2(300, 0), max_distance=200)


def test_enemy_chase():
    e = Enemy(entity_id="slime_1", pos=Vector2(0, 0))
    e.start_chase(Vector2(100, 0))
    assert e.state == "chase"
    assert e.vel.x > 0
    e.stop_chase()
    assert e.state == "patrol"


if __name__ == "__main__":
    test_enemy_patrol()
    test_enemy_can_see()
    test_enemy_chase()
    print("All enemy tests passed!")
