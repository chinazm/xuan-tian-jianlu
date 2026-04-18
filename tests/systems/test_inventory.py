import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from systems.inventory import Inventory
from core.event_bus import EventBus


def test_add_item():
    EventBus.clear()
    inv = Inventory()
    assert inv.add_item("hp_potion")
    assert inv._items[0].quantity == 1
    assert inv.add_item("hp_potion")
    assert inv._items[0].quantity == 2


def test_use_item():
    EventBus.clear()
    inv = Inventory()
    inv.add_item("hp_potion", quantity=2)
    effect = inv.use_item("hp_potion")
    assert effect == {"hp_restore_pct": 0.5}
    assert inv._items[0].quantity == 1


def test_equip():
    EventBus.clear()
    inv = Inventory()
    old = inv.equip("bamboo_sword")
    assert old is None
    stats = inv.get_equipped_stats()
    assert stats["atk"] == 5


if __name__ == "__main__":
    test_add_item()
    test_use_item()
    test_equip()
    print("All inventory tests passed!")
