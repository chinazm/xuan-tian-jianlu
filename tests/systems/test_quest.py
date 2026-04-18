import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from systems.quest import QuestSystem
from core.event_bus import EventBus


def test_start_quest():
    EventBus.clear()
    qs = QuestSystem()
    quest = qs.start_quest("MAIN_CH02_001")
    assert quest is not None
    assert quest.active
    assert len(qs.active_quests) == 1


def test_update_from_event():
    EventBus.clear()
    qs = QuestSystem()
    qs.start_quest("MAIN_CH02_001")
    for _ in range(3):
        qs.update_from_event("entity_die", "bamboo_demon")
    assert qs.active_quests[0].completed
    assert "MAIN_CH02_001" in qs.completed_quests


if __name__ == "__main__":
    test_start_quest()
    test_update_from_event()
    print("All quest tests passed!")
