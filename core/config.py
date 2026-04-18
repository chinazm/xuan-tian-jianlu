"""核心配置常量。引擎默认值，可通过 config/settings.json 覆盖。
所有参数都是通用的，不绑定任何游戏特定内容。
"""
from dataclasses import dataclass, field


@dataclass
class WindowConfig:
    width: int = 800
    height: int = 600
    title: str = "Game"
    fps: int = 60
    fullscreen: bool = False


@dataclass
class RenderConfig:
    tile_size: int = 32
    camera_smooth: float = 0.1


@dataclass
class PhysicsConfig:
    """物理参数（通用，不绑定游戏内容）"""
    player_base_speed: float = 120.0
    player_acceleration: float = 800.0
    player_deceleration: float = 1000.0
    knockback_force: float = 80.0
    knockback_duration: float = 0.15
    dodge_distance: float = 60.0
    dodge_duration: float = 0.2
    dodge_cooldown: float = 0.8


@dataclass
class CombatConfig:
    """战斗参数（通用）"""
    default_attack_cooldown: float = 0.5
    default_attack_range: float = 40.0
    invincibility_duration: float = 0.5
    i_frame_flash_speed: float = 10.0


@dataclass
class GameConfig:
    window: WindowConfig = field(default_factory=WindowConfig)
    render: RenderConfig = field(default_factory=RenderConfig)
    physics: PhysicsConfig = field(default_factory=PhysicsConfig)
    combat: CombatConfig = field(default_factory=CombatConfig)

    @classmethod
    def from_json(cls, path: str) -> "GameConfig":
        """从 JSON 配置文件加载配置，覆盖默认值。"""
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cfg = cls()
        if "window" in data:
            for k, v in data["window"].items():
                if hasattr(cfg.window, k):
                    setattr(cfg.window, k, v)
        if "render" in data:
            for k, v in data["render"].items():
                if hasattr(cfg.render, k):
                    setattr(cfg.render, k, v)
        return cfg
