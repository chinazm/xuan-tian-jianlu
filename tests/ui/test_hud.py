import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from ui.hud import HUD


def test_hud_render():
    pygame.init()
    pygame.display.set_mode((800, 600))
    hud = HUD()
    screen = pygame.Surface((800, 600))
    state = {
        "current_hp": 80, "max_hp": 100,
        "current_mp": 50, "max_mp": 100,
        "realm": "炼气期", "realm_level": 3,
        "lingshi": 150,
        "skills": ["普通攻击", "御剑术"],
    }
    hud.render(screen, state)
    pygame.quit()
    print("HUD render test passed!")


if __name__ == "__main__":
    test_hud_render()
    print("All HUD tests passed!")
