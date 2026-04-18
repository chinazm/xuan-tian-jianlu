import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
from world.room import Room


def test_room_load():
    test_dir = Path("tests/test_room")
    test_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "id": "test_room",
        "name": "测试房间",
        "tiles": [[0,0],[0,0],[0,0]],
        "portals": [{"pos": [0, 1], "target": "next_room", "target_pos": [5, 1], "label": "前进"}],
        "enemies": [{"type": "slime", "pos": [2, 1]}],
        "items": [{"type": "hp_potion", "pos": [1, 1]}],
    }
    with open(test_dir / "test.json", "w") as f:
        json.dump(data, f)
    room = Room.from_json(str(test_dir / "test.json"))
    assert room is not None
    assert room.room_id == "test_room"
    assert room.name == "测试房间"
    assert len(room.portals) == 1
    assert room.portals[0].target_room == "next_room"
    assert len(room.enemies) == 1
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    print("Room load test passed!")


if __name__ == "__main__":
    test_room_load()
    print("All room tests passed!")
