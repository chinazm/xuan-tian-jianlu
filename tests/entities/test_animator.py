import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from entities.animator import Animator, Animation


def _make_surface(color):
    s = pygame.Surface((16, 16))
    s.fill(color)
    return s


def test_play_animation():
    pygame.init()
    pygame.display.set_mode((1, 1))
    anim = Animator()
    anim.add(Animation("walk", [_make_surface((255, 0, 0)), _make_surface((0, 255, 0))], frame_duration=0.1))
    anim.play("walk")
    assert anim.current_frame is not None
    pygame.quit()


def test_animation_loop():
    pygame.init()
    pygame.display.set_mode((1, 1))
    anim = Animator()
    frames = [_make_surface((255, 0, 0)), _make_surface((0, 255, 0)), _make_surface((0, 0, 255))]
    anim.add(Animation("run", frames, frame_duration=0.1, loop=True))
    anim.play("run")
    for _ in range(5):
        anim.update(0.11)
    assert not anim.is_finished
    pygame.quit()


def test_non_looping_animation():
    pygame.init()
    pygame.display.set_mode((1, 1))
    anim = Animator()
    anim.add(Animation("attack", [_make_surface((255, 0, 0)), _make_surface((0, 255, 0))], frame_duration=0.1, loop=False))
    anim.play("attack")
    anim.update(0.11)
    anim.update(0.11)
    assert anim.is_finished
    pygame.quit()


def test_play_same_animation_doesnt_reset():
    pygame.init()
    pygame.display.set_mode((1, 1))
    anim = Animator()
    anim.add(Animation("idle", [_make_surface((255, 0, 0))]))
    anim.play("idle")
    anim.play("idle")  # should not reset
    assert anim._frame_index == 0
    pygame.quit()


if __name__ == "__main__":
    test_play_animation()
    test_animation_loop()
    test_non_looping_animation()
    test_play_same_animation_doesnt_reset()
    print("All animator tests passed!")
