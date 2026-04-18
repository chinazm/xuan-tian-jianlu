"""输入处理系统测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.input_handler import InputHandler


class MockKeys:
    def __init__(self, pressed=None):
        self._pressed = set(pressed or [])

    def __call__(self):
        return self

    def __getitem__(self, key):
        return key in self._pressed


def test_no_input():
    import pygame
    orig_get_pressed = pygame.key.get_pressed
    pygame.key.get_pressed = MockKeys()

    handler = InputHandler()
    handler.update(0.016)

    assert handler.direction.x == 0
    assert handler.direction.y == 0
    assert not handler.is_direction_held()

    pygame.key.get_pressed = orig_get_pressed


def test_directional_input():
    import pygame
    pressed_keys = {pygame.K_w: True, pygame.K_d: True}
    pygame.key.get_pressed = MockKeys(pressed_keys)

    handler = InputHandler()
    handler.update(0.016)

    assert handler.direction.x > 0
    assert handler.direction.y < 0
    assert handler.is_direction_held()

    pygame.key.get_pressed = MockKeys()
    handler.update(0.016)
    assert not handler.is_direction_held()

    pygame.key.get_pressed = MockKeys()


def test_action_buffer():
    import pygame
    # 第一帧：按下 j (attack)
    pygame.key.get_pressed = MockKeys({pygame.K_j: True})
    handler = InputHandler()
    handler.update(0.016)

    assert handler.consume_action("attack") is True
    assert handler.consume_action("attack") is False

    # 第二帧：继续按住 j，不应再次触发
    pygame.key.get_pressed = MockKeys({pygame.K_j: True})
    handler.update(0.016)
    assert handler.consume_action("attack") is False

    # 第三帧：松开后再按下
    pygame.key.get_pressed = MockKeys()
    handler.update(0.016)
    pygame.key.get_pressed = MockKeys({pygame.K_j: True})
    handler.update(0.016)
    assert handler.consume_action("attack") is True

    pygame.key.get_pressed = MockKeys()


def test_buffer_max():
    import pygame
    pygame.key.get_pressed = MockKeys()
    handler = InputHandler(buffer_max=3)

    # 模拟连续按下不同键
    keys_to_press = [pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_e]
    for key in keys_to_press:
        pygame.key.get_pressed = MockKeys()
        handler.update(0.016)
        pygame.key.get_pressed = MockKeys({key: True})
        handler.update(0.016)

    assert len(handler.action_buffer) <= 3

    pygame.key.get_pressed = MockKeys()


def test_is_action_just_pressed():
    import pygame
    pygame.key.get_pressed = MockKeys({pygame.K_j: True})
    handler = InputHandler()
    handler.update(0.016)

    assert handler.is_action_just_pressed("attack") is True
    assert handler.is_action_just_pressed("skill") is False

    pygame.key.get_pressed = MockKeys()


if __name__ == "__main__":
    test_no_input()
    test_directional_input()
    test_action_buffer()
    test_buffer_max()
    test_is_action_just_pressed()
    print("All input handler tests passed!")
