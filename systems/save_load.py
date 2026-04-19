"""存档系统：JSON 序列化存档、版本校验、多存档位。"""
import json
import os
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from core.logger import GameLogger

logger = GameLogger.get("save")

def get_save_dir() -> Path:
    """获取存档目录，兼容桌面和 Android APK 环境。"""
    try:
        import android  # noqa: F401
        # Android 环境下使用当前工作目录（p4a 设置为应用私有目录）
        import os
        return Path(os.getcwd()) / "saves"
    except (ImportError, RuntimeError, OSError):
        # 桌面环境使用相对路径
        return Path("saves")

SAVE_DIR = get_save_dir()
SCHEMA_VERSION = 1


@dataclass
class SaveData:
    schema_version: int = SCHEMA_VERSION
    player_name: str = "林凡"
    realm: str = "炼气期"
    realm_level: int = 1
    lingli: float = 0.0
    max_hp: float = 100
    current_hp: float = 100
    atk: float = 10
    def_: float = 2
    current_room: str = "sect_main"
    player_pos: list = field(default_factory=lambda: [0.0, 0.0])
    inventory: list = field(default_factory=list)
    equipment: dict = field(default_factory=dict)
    lingshi: int = 0
    completed_quests: list = field(default_factory=list)
    play_time: float = 0.0
    checksum: str = ""

    def compute_checksum(self) -> str:
        data = {k: v for k, v in asdict(self).items() if k != "checksum"}
        return hashlib.md5(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def save(self, slot: int) -> bool:
        SAVE_DIR.mkdir(exist_ok=True)
        self.checksum = self.compute_checksum()
        path = SAVE_DIR / f"slot_{slot}.json"
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, ensure_ascii=False, indent=2)
            logger.info(f"Saved to slot {slot}")
            return True
        except Exception as e:
            logger.error(f"Save failed: {e}")
            return False

    @classmethod
    def load(cls, slot: int) -> Optional["SaveData"]:
        path = SAVE_DIR / f"slot_{slot}.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        saved_checksum = data.pop("checksum", "")
        calc_checksum = hashlib.md5(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if saved_checksum != calc_checksum:
            logger.error(f"Slot {slot} corrupted!")
            return None
        return cls(**data)

    @classmethod
    def slot_exists(cls, slot: int) -> bool:
        return (SAVE_DIR / f"slot_{slot}.json").exists()
