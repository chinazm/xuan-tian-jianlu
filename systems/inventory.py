"""背包与装备系统。"""
from dataclasses import dataclass, field
from typing import Optional
import json
from pathlib import Path
from core.event_bus import EventBus


@dataclass
class Item:
    item_id: str
    name: str
    type: str  # "consumable", "material", "key"
    description: str = ""
    stackable: bool = True
    max_stack: int = 99
    quantity: int = 1


@dataclass
class Equipment:
    item_id: str
    name: str
    slot: str  # "weapon", "armor", "accessory"
    atk_bonus: int = 0
    def_bonus: int = 0
    hp_bonus: int = 0
    description: str = ""


class Inventory:
    def __init__(self, max_slots: int = 20, data_path: str = "data/items.json"):
        self.max_slots = max_slots
        self._items: list[Item] = []
        self._equipment_slots: dict[str, Optional[Equipment]] = {
            "weapon": None, "armor": None, "accessory": None,
        }
        self.lingshi: int = 0
        self._item_defs: dict = {}
        self._equip_defs: dict = {}
        self._load_data(data_path)

    def _load_data(self, path: str) -> None:
        p = Path(path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._item_defs = data.get("items", {})
            self._equip_defs = data.get("equipment", {})

    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        if item_id in self._item_defs:
            defn = self._item_defs[item_id]
            existing = None
            for item in self._items:
                if item.item_id == item_id and item.quantity < item.max_stack:
                    existing = item
                    break
            if existing:
                add = min(quantity, existing.max_stack - existing.quantity)
                existing.quantity += add
            elif len(self._items) < self.max_slots:
                item = Item(item_id=item_id, name=defn.get("name", item_id),
                           type=defn.get("type", "material"), description=defn.get("description", ""),
                           max_stack=defn.get("max_stack", 99), quantity=quantity)
                self._items.append(item)
            else:
                return False
            EventBus.publish("item_pickup", {"item_id": item_id, "quantity": quantity})
            return True
        return False

    def use_item(self, item_id: str) -> Optional[dict]:
        for i, item in enumerate(self._items):
            if item.item_id == item_id:
                effect = self._item_defs.get(item_id, {}).get("effect", {})
                item.quantity -= 1
                if item.quantity <= 0:
                    self._items.pop(i)
                return effect
        return None

    def equip(self, equip_id: str) -> Optional[Equipment]:
        if equip_id in self._equip_defs:
            defn = self._equip_defs[equip_id]
            slot = defn.get("slot", "weapon")
            equip = Equipment(item_id=equip_id, name=defn.get("name", equip_id),
                             slot=slot, atk_bonus=defn.get("atk", 0),
                             def_bonus=defn.get("def", 0), hp_bonus=defn.get("hp", 0))
            old = self._equipment_slots[slot]
            self._equipment_slots[slot] = equip
            return old
        return None

    def get_equipped_stats(self) -> dict:
        atk = def_ = hp = 0
        for eq in self._equipment_slots.values():
            if eq:
                atk += eq.atk_bonus
                def_ += eq.def_bonus
                hp += eq.hp_bonus
        return {"atk": atk, "def": def_, "hp": hp}
