import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import json
import pygame
from world.tilemap import Tilemap
from core.resource_manager import ResourceManager


def _make_tileset():
    surf = pygame.Surface((96, 64))
    for r in range(2):
        for c in range(3):
            tile = surf.subsurface(pygame.Rect(c*32, r*32, 32, 32))
            tile.fill((r*80, c*80, 100))
    return surf


def test_tilemap_load():
    pygame.init()
    pygame.display.set_mode((1, 1))

    test_dir = Path("tests/test_world")
    test_dir.mkdir(parents=True, exist_ok=True)

    map_data = {
        "tiles": [
            [1,1,1],
            [1,0,1],
            [1,1,1]
        ],
        "collision_tiles": [1]
    }
    with open(test_dir / "test.json", "w") as f:
        json.dump(map_data, f)

    _make_tileset()
    ts = _make_tileset()
    pygame.image.save(ts, str(test_dir / "tiles.png"))

    rm = ResourceManager(base_path=str(test_dir))
    tm = Tilemap(rm, tile_size=32)
    tm.load(str(test_dir / "test.json"), "tiles.png", collision_tile_ids=[1])

    assert tm.width == 3
    assert tm.height == 3
    assert tm.pixel_width == 96
    assert tm.pixel_height == 96
    assert tm.get_tile(1, 1) == 0
    assert tm.get_tile(0, 0) == 1
    assert tm.is_collision_tile(1) is True
    assert tm.is_collision_tile(0) is False

    rects = tm.get_collision_rects()
    assert len(rects) == 8

    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    pygame.quit()
    print("Tilemap load test passed!")


if __name__ == "__main__":
    test_tilemap_load()
    print("All tilemap tests passed!")
