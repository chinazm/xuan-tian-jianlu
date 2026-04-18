import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from systems.dialogue import DialogueSystem


def test_start_dialogue():
    ds = DialogueSystem()
    assert ds.start("master_greeting")
    assert ds.is_active()


def test_get_choices():
    ds = DialogueSystem()
    ds.start("master_greeting")
    assert ds.has_choices()
    assert len(ds.get_choices()) == 2


def test_next_branch():
    ds = DialogueSystem()
    ds.start("master_greeting")
    result = ds.next(choice_index=0)
    assert result == "master_praise"
    assert ds.is_active()
    ds.next()  # finish
    assert not ds.is_active()


if __name__ == "__main__":
    test_start_dialogue()
    test_get_choices()
    test_next_branch()
    print("All dialogue tests passed!")
