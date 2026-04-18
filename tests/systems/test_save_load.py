import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from systems.save_load import SaveData
import shutil


def test_save_and_load():
    save_dir = Path("tests/test_saves")
    # Temporarily override SAVE_DIR
    import systems.save_load as sl
    orig = sl.SAVE_DIR
    sl.SAVE_DIR = save_dir
    sl.SAVE_DIR.mkdir(exist_ok=True)

    sd = SaveData(player_name="test", realm="筑基期", realm_level=2)
    assert sd.save(1)

    loaded = SaveData.load(1)
    assert loaded is not None
    assert loaded.player_name == "test"
    assert loaded.realm == "筑基期"

    shutil.rmtree(save_dir, ignore_errors=True)
    sl.SAVE_DIR = orig
    print("Save/load test passed!")


def test_corrupted_save():
    import systems.save_load as sl
    save_dir = Path("tests/test_saves_corrupt")
    orig = sl.SAVE_DIR
    sl.SAVE_DIR = save_dir
    save_dir.mkdir(exist_ok=True)

    # Write invalid data
    with open(save_dir / "slot_2.json", "w") as f:
        f.write('{"player_name": "hacked", "checksum": "invalid"}')

    loaded = SaveData.load(2)
    assert loaded is None

    shutil.rmtree(save_dir, ignore_errors=True)
    sl.SAVE_DIR = orig
    print("Corrupted save test passed!")


if __name__ == "__main__":
    test_save_and_load()
    test_corrupted_save()
    print("All save/load tests passed!")
