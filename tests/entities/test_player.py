import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from entities.player import Player
from core.vector import Vector2
from core.input_handler import InputHandler


class MockInput:
    def __init__(self, direction=None, actions=None):
        self._direction = Vector2(*direction) if direction else Vector2(0, 0)
        self._actions = list(actions or [])

    def consume_action(self, name):
        if name in self._actions:
            self._actions.remove(name)
            return True
        return False

    def is_direction_held(self):
        return self._direction.length() > 0

    @property
    def direction(self):
        return self._direction


def test_player_creation():
    p = Player(pos=Vector2(100, 100))
    assert p.pos.x == 100
    assert p.is_alive
    assert p.state == "idle"


def test_player_move():
    pygame.init()
    p = Player(pos=Vector2(0, 0))
    inp = MockInput(direction=(1, 0))
    p.handle_input(inp, 0.016)
    assert p.state == "walk"
    assert p.vel.x > 0
    pygame.quit()


def test_player_attack():
    pygame.init()
    p = Player(pos=Vector2(0, 0))
    inp = MockInput(actions=["attack"])
    p.handle_input(inp, 0.016)
    assert p.state == "attack"
    assert p.attack_timer > 0
    pygame.quit()


def test_player_dodge():
    pygame.init()
    p = Player(pos=Vector2(0, 0))
    inp = MockInput(direction=(1, 0), actions=["dodge"])
    p.handle_input(inp, 0.016)
    assert p.state == "dodge"
    assert p.invincible
    assert p.dodge_cooldown > 0
    pygame.quit()


def test_attack_rect():
    pygame.init()
    p = Player(pos=Vector2(100, 100))
    p.facing = "right"
    rect = p.get_attack_rect()
    assert rect.x > 100
    pygame.quit()


if __name__ == "__main__":
    test_player_creation()
    test_player_move()
    test_player_attack()
    test_player_dodge()
    test_attack_rect()
    print("All player tests passed!")
