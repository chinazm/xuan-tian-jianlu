import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import json
import pygame
from entities.factory import EntityFactory
from core.resource_manager import ResourceManager
from core.vector import Vector2


def test_entity_factory():
    pygame.init()
    pygame.display.set_mode((1, 1))

    test_dir = Path("tests/test_factory")
    test_dir.mkdir(parents=True, exist_ok=True)

    entities_data = {
        "player": {
            "name": "主角",
            "size": [32, 32],
            "max_hp": 100,
            "base_speed": 120,
            "sprite_sheet": "player.png"
        },
        "slime": {
            "name": "史莱姆",
            "size": [32, 32],
            "max_hp": 30,
            "base_speed": 40
        }
    }
    with open(test_dir / "entities.json", "w") as f:
        json.dump(entities_data, f)

    sheet = pygame.Surface((128, 32))
    sheet.fill((0, 255, 0))
    pygame.image.save(sheet, str(test_dir / "player.png"))

    rm = ResourceManager(base_path=str(test_dir))
    factory = EntityFactory(rm, data_path=str(test_dir))

    assert "player" in factory.get_entity_types()
    assert "slime" in factory.get_entity_types()

    player = factory.create("player", Vector2(0, 0))
    assert player is not None
    assert player.max_hp == 100
    assert player.base_speed == 120

    slime = factory.create("slime", Vector2(100, 100))
    assert slime is not None
    assert slime.max_hp == 30
    assert slime.base_speed == 40

    unknown = factory.create("unknown", Vector2(0, 0))
    assert unknown is None

    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    pygame.quit()
    print("Entity factory test passed!")


if __name__ == "__main__":
    test_entity_factory()
    print("All factory tests passed!")
