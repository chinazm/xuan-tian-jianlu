"""资源管理器测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
import shutil
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from core.resource_manager import ResourceManager

TEST_DIR = Path("tests/test_assets")


def test_cache_lru_eviction():
    pygame.init()
    pygame.display.set_mode((1, 1))

    TEST_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(5):
        surf = pygame.Surface((16, 16))
        surf.fill((255, 0, 0))
        pygame.image.save(surf, str(TEST_DIR / f"test_{i}.png"))

    mgr = ResourceManager(max_cache_size=3, base_path="tests/test_assets")

    for i in range(5):
        mgr.load(f"test_{i}.png")

    info = mgr.cache_info()
    assert info["cached"] == 3

    for i in range(5):
        (TEST_DIR / f"test_{i}.png").unlink(missing_ok=True)
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    pygame.quit()


def test_spritesheet_split():
    pygame.init()
    pygame.display.set_mode((1, 1))

    TEST_DIR.mkdir(parents=True, exist_ok=True)

    sheet = pygame.Surface((64, 32))
    sheet.fill((255, 0, 0))
    subsurf = sheet.subsurface((32, 0, 32, 32))
    subsurf.fill((0, 255, 0))
    pygame.image.save(sheet, str(TEST_DIR / "test_sheet.png"))

    mgr = ResourceManager(max_cache_size=10, base_path="tests/test_assets")
    frames = mgr.load_spritesheet("test_sheet.png", tile_w=32, tile_h=32)

    assert len(frames) == 2

    (TEST_DIR / "test_sheet.png").unlink(missing_ok=True)
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    pygame.quit()


def test_file_not_found():
    pygame.init()
    mgr = ResourceManager(base_path="tests/test_assets")
    try:
        mgr.load("nonexistent.png")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass
    pygame.quit()


def test_preload_paths_ignores_missing():
    pygame.init()
    mgr = ResourceManager(base_path="tests/test_assets")
    mgr.preload_paths(["missing1.png", "missing2.png"])  # Should not raise
    pygame.quit()


if __name__ == "__main__":
    test_cache_lru_eviction()
    test_spritesheet_split()
    test_file_not_found()
    test_preload_paths_ignores_missing()
    print("All resource manager tests passed!")
