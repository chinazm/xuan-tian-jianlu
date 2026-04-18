"""实体工厂：从 JSON 数据实例化实体。"""
import json
from pathlib import Path
from typing import Optional
from core.vector import Vector2
from core.resource_manager import ResourceManager
from entities.entity import Entity


class EntityFactory:
    def __init__(self, resource_mgr: ResourceManager, data_path: str = "data"):
        self._resource_mgr = resource_mgr
        self._data_path = Path(data_path)
        self._entity_defs: dict = {}
        self._load_definitions()

    def _load_definitions(self) -> None:
        entities_file = self._data_path / "entities.json"
        if entities_file.exists():
            with open(entities_file, "r", encoding="utf-8") as f:
                self._entity_defs = json.load(f)

    def create(self, entity_type: str, pos: Vector2) -> Optional[Entity]:
        if entity_type not in self._entity_defs:
            return None

        defn = self._entity_defs[entity_type]
        size = Vector2(*defn.get("size", [32, 32]))

        entity = Entity(
            entity_id=f"{entity_type}_{pos.x}_{pos.y}",
            pos=pos,
            size=size,
            max_hp=defn.get("max_hp", 100),
            current_hp=defn.get("max_hp", 100),
            base_speed=defn.get("base_speed", 100),
        )

        sheet_path = defn.get("sprite_sheet")
        if sheet_path:
            try:
                frames = self._resource_mgr.load_spritesheet(
                    sheet_path, size.x, size.y
                )
                entity.animation_frames = frames
                entity.sprite = frames[0] if frames else None
            except FileNotFoundError:
                pass

        return entity

    def get_entity_types(self) -> list[str]:
        return list(self._entity_defs.keys())
