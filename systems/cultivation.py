"""修炼系统：灵力积累、境界突破。"""
import json
import random
from pathlib import Path
from core.event_bus import EventBus
from core.logger import GameLogger

logger = GameLogger.get("cultivation")


class CultivationSystem:
    def __init__(self, data_path: str = "data/realms.json"):
        self._realms: list[dict] = []
        self._load_realms(data_path)
        self.current_realm_index = 0
        self.realm_level = 1
        self.lingli = 0.0
        self.cultivating = False
        self.cultivation_speed = 1.0

    def _load_realms(self, path: str) -> None:
        p = Path(path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                self._realms = json.load(f)

    @property
    def current_realm_name(self) -> str:
        if not self._realms:
            return "未知"
        return self._realms[self.current_realm_index].get("name", "未知")

    @property
    def current_realm_data(self) -> dict:
        return self._realms[self.current_realm_index]

    @property
    def max_level_in_realm(self) -> int:
        exp_list = self.current_realm_data.get("exp_to_next", [])
        return len(exp_list)

    def add_lingli(self, amount: float) -> None:
        self.lingli += amount * self.cultivation_speed
        if self._check_breakthrough():
            pass

    def _check_breakthrough(self) -> bool:
        exp_list = self.current_realm_data.get("exp_to_next", [])
        if self.realm_level > len(exp_list):
            return False
        required = exp_list[self.realm_level - 1]
        if self.lingli >= required:
            chance = self.current_realm_data.get("breakthrough_chance", 0.7)
            if random.random() < chance:
                self._breakthrough()
                return True
            else:
                self.lingli *= 0.5
                EventBus.publish("breakthrough_fail", {"realm": self.current_realm_name, "level": self.realm_level})
        return False

    def _breakthrough(self) -> None:
        exp_list = self.current_realm_data.get("exp_to_next", [])
        self.realm_level += 1
        if self.realm_level > len(exp_list):
            self.current_realm_index += 1
            if self.current_realm_index >= len(self._realms):
                self.current_realm_index = len(self._realms) - 1
                self.realm_level = len(exp_list)
                return
            self.realm_level = 1
        EventBus.publish("level_up", {"realm": self.current_realm_name, "level": self.realm_level})

    def get_stat_bonus(self, stat_name: str) -> float:
        data = self.current_realm_data
        return data.get(f"base_{stat_name}", 0)

    def get_progress(self) -> float:
        exp_list = self.current_realm_data.get("exp_to_next", [])
        if self.realm_level > len(exp_list):
            return 1.0
        required = exp_list[self.realm_level - 1]
        if required == 0:
            return 1.0
        return min(1.0, self.lingli / required)

    def has_realms(self) -> bool:
        return bool(self._realms)

    def find_realm_index(self, realm_name: str) -> int:
        for idx, realm_data in enumerate(self._realms):
            if realm_data.get("name") == realm_name:
                return idx
        return 0
