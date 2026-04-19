import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from core.config import GameConfig
from core.game import GameScene


def test_game_scene_loads_from_base_dir_when_cwd_changes(monkeypatch, tmp_path):
    pygame.init()
    pygame.display.set_mode((1, 1))

    repo_root = Path(__file__).resolve().parents[2]
    monkeypatch.chdir(tmp_path)

    scene = GameScene(GameConfig(), room_id="ch01_qingshi_town", base_dir=repo_root)

    try:
        scene.on_enter()

        assert scene.room is not None
        assert scene.player is not None

        scene.update(0.016)
    finally:
        scene.on_exit()
        pygame.quit()
