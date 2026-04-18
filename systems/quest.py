"""任务系统：目标追踪、条件检查、奖励发放。"""
from dataclasses import dataclass, field
import json
from pathlib import Path
from core.event_bus import EventBus


@dataclass
class QuestObjective:
    type: str  # "kill", "collect", "talk", "reach", "cultivate"
    target: str
    required: int
    current: int = 0

    def is_complete(self) -> bool:
        return self.current >= self.required


@dataclass
class Quest:
    quest_id: str
    title: str
    description: str
    giver_npc: str
    objectives: list[QuestObjective]
    reward_lingshi: int = 0
    reward_items: list[str] = field(default_factory=list)
    completed: bool = False
    active: bool = False

    def check_completion(self) -> bool:
        if not self.objectives:
            return False
        return all(obj.is_complete() for obj in self.objectives)

    def to_dict(self) -> dict:
        return {
            "quest_id": self.quest_id, "title": self.title,
            "description": self.description, "giver_npc": self.giver_npc,
            "completed": self.completed, "active": self.active,
        }


class QuestSystem:
    def __init__(self, data_path: str = "data/quests.json"):
        self._quest_defs: dict = {}
        self.active_quests: list[Quest] = []
        self.completed_quests: list[str] = []
        p = Path(data_path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                self._quest_defs = json.load(f)

    def start_quest(self, quest_id: str):
        if quest_id not in self._quest_defs or quest_id in self.completed_quests:
            return None
        defn = self._quest_defs[quest_id]
        objectives = [QuestObjective(**obj) for obj in defn.get("objectives", [])]
        quest = Quest(quest_id=quest_id, title=defn.get("title", ""),
                     description=defn.get("description", ""),
                     giver_npc=defn.get("giver_npc", ""),
                     objectives=objectives,
                     reward_lingshi=defn.get("reward", {}).get("lingshi", 0),
                     reward_items=defn.get("reward", {}).get("items", []))
        quest.active = True
        self.active_quests.append(quest)
        EventBus.publish("quest_start", {"quest_id": quest_id})
        return quest

    def update_from_event(self, event_name: str, target_id: str) -> None:
        type_map = {"entity_die": "kill", "item_pickup": "collect", "level_up": "cultivate"}
        obj_type = type_map.get(event_name)
        if not obj_type:
            return
        for quest in self.active_quests:
            if quest.completed:
                continue
            for obj in quest.objectives:
                if obj.type == obj_type and obj.target == target_id:
                    obj.current += 1
                    if obj.is_complete() and quest.check_completion():
                        quest.completed = True
                        self.completed_quests.append(quest.quest_id)
                        EventBus.publish("quest_complete", {"quest_id": quest.quest_id})
