import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.camera import Camera
from core.vector import Vector2


def test_camera_follow():
    cam = Camera(800, 600)
    target = Vector2(400, 300)
    for _ in range(100):
        cam.follow(target, 0.016)

    assert abs(cam.pos.x - 0) < 1
    assert abs(cam.pos.y - 0) < 1


def test_camera_bounds():
    cam = Camera(800, 600)
    cam.set_bounds(1600, 1200)

    target = Vector2(1500, 1100)
    for _ in range(100):
        cam.follow(target, 0.016)

    assert cam.pos.x >= 0
    assert cam.pos.y >= 0
    assert cam.pos.x + cam.width <= 1600
    assert cam.pos.y + cam.height <= 1200


def test_world_to_screen():
    cam = Camera(800, 600)
    cam.pos = Vector2(100, 50)

    screen_pos = cam.apply(Vector2(200, 150))
    assert screen_pos.x == 100
    assert screen_pos.y == 100


def test_visibility_check():
    cam = Camera(800, 600)
    cam.pos = Vector2(0, 0)

    assert cam.is_visible(Vector2(100, 100), Vector2(32, 32))
    assert not cam.is_visible(Vector2(-100, 100), Vector2(32, 32))
    assert not cam.is_visible(Vector2(900, 100), Vector2(32, 32))


def test_world_rect():
    cam = Camera(800, 600)
    cam.pos = Vector2(100, 50)
    rect = cam.world_rect()
    assert rect == (100, 50, 900, 650)


if __name__ == "__main__":
    test_camera_follow()
    test_camera_bounds()
    test_world_to_screen()
    test_visibility_check()
    test_world_rect()
    print("All camera tests passed!")
