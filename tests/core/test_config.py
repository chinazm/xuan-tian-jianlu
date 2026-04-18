"""配置模块单元测试"""
import json
import tempfile
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import GameConfig, WindowConfig


def test_default_config():
    cfg = GameConfig()
    assert cfg.window.width == 800
    assert cfg.window.fps == 60
    assert cfg.render.tile_size == 32
    assert cfg.physics.player_base_speed == 120.0
    assert cfg.combat.default_attack_cooldown == 0.5


def test_load_from_json():
    data = {
        "window": {"width": 1024, "height": 768, "title": "Test"},
        "render": {"tile_size": 16}
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.flush()
        cfg = GameConfig.from_json(f.name)

    assert cfg.window.width == 1024
    assert cfg.window.height == 768
    assert cfg.window.title == "Test"
    assert cfg.render.tile_size == 16
    # 未设置的字段保持默认值
    assert cfg.window.fps == 60


def test_unknown_keys_ignored():
    """未知配置键不应报错"""
    data = {"window": {"unknown_key": "value", "width": 640}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.flush()
        cfg = GameConfig.from_json(f.name)

    assert cfg.window.width == 640
    assert cfg.window.height == 600  # 保持默认


if __name__ == "__main__":
    test_default_config()
    test_load_from_json()
    test_unknown_keys_ignored()
    print("All config tests passed!")
