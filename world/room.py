"""房间/场景管理：实体初始化、传送门、区域切换。"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from core.vector import Vector2
from core.logger import GameLogger

logger = GameLogger.get("room")


@dataclass
class Portal:
    pos: Vector2
    target_room: str
    target_pos: Vector2
    label: str = ""


class Room:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.name = ""
        self.size = Vector2(0, 0)
        self.portals: list[Portal] = []
        self.enemies: list[dict] = []
        self.items: list[dict] = []
        self.npcs: list[dict] = []
        self.music: str = ""
        self.realm_require: str = ""

    @classmethod
    def from_json(cls, path: str) -> Optional["Room"]:
        p = Path(path)
        if not p.exists():
            return None
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        room = cls(data.get("id", "unknown"))
        room.name = data.get("name", "")
        tiles = data.get("tiles", [])
        room.size = Vector2(len(tiles[0]) if tiles else 0, len(tiles))
        for portal_data in data.get("portals", []):
            room.portals.append(Portal(
                pos=Vector2(*portal_data["pos"]),
                target_room=portal_data["target"],
                target_pos=Vector2(*portal_data["target_pos"]),
                label=portal_data.get("label", ""),
            ))
        room.enemies = data.get("enemies", [])
        room.items = data.get("items", [])
        room.npcs = data.get("npcs", [])
        room.music = data.get("music", "")
        room.realm_require = data.get("realm_require", "")
        return room
