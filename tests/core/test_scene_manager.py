import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from core.scene_manager import SceneManager, Scene


class TestScene(Scene):
    def __init__(self, name: str):
        super().__init__(name)
        self.update_count = 0
        self.entered = False
        self.exited = False

    def on_enter(self):
        super().on_enter()
        self.entered = True

    def on_exit(self):
        super().on_exit()
        self.exited = True

    def update(self, dt: float):
        self.update_count += 1


def test_register_and_switch():
    pygame.init()
    sm = SceneManager()
    s1 = TestScene("scene1")
    s2 = TestScene("scene2")

    sm.register(s1)
    sm.register(s2)

    sm.set_immediate("scene1")
    assert sm.current_scene_name == "scene1"
    assert s1.entered

    sm.set_immediate("scene2")
    assert sm.current_scene_name == "scene2"
    assert s1.exited
    assert s2.entered

    pygame.quit()


def test_fade_transition():
    pygame.init()
    sm = SceneManager()
    s1 = TestScene("scene1")
    s2 = TestScene("scene2")

    sm.register(s1)
    sm.register(s2)
    sm.set_immediate("scene1")

    sm.switch_to("scene2", fade_duration=0.5)
    assert sm._transition["phase"] == "fade_out"
    assert sm.current_scene_name == "scene1"  # 还没切换

    # 模拟 fade_out 完成
    for _ in range(40):
        sm.update(0.016)

    assert sm.current_scene_name == "scene2"
    assert s1.exited
    assert s2.entered

    # fade_in 完成
    for _ in range(40):
        sm.update(0.016)

    assert sm._transition is None

    pygame.quit()


def test_invalid_scene_switch():
    sm = SceneManager()
    sm.switch_to("nonexistent")  # Should not raise, just log error


def test_scene_update():
    pygame.init()
    sm = SceneManager()
    s1 = TestScene("scene1")
    sm.register(s1)
    sm.set_immediate("scene1")

    for _ in range(10):
        sm.update(0.016)

    assert s1.update_count == 10

    pygame.quit()


if __name__ == "__main__":
    test_register_and_switch()
    test_fade_transition()
    test_invalid_scene_switch()
    test_scene_update()
    print("All scene manager tests passed!")
