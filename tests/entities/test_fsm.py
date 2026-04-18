import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from entities.fsm import FSM, State


def test_state_transitions():
    fsm = FSM()
    transitions = []
    fsm.add_state(State("idle", on_enter=lambda p: transitions.append("enter_idle"), on_exit=lambda: transitions.append("exit_idle")))
    fsm.add_state(State("walk", on_enter=lambda p: transitions.append(f"enter_walk_{p.get('dir', '')}")))
    fsm.set_state("idle")
    assert fsm.current_state == "idle"
    assert transitions == ["enter_idle"]
    fsm.set_state("walk", {"dir": "right"})
    assert fsm.current_state == "walk"
    assert transitions == ["enter_idle", "exit_idle", "enter_walk_right"]


def test_state_update():
    fsm = FSM()
    count = [0]
    fsm.add_state(State("move", on_update=lambda dt, p: count.__setitem__(0, count[0] + 1)))
    fsm.set_state("move")
    fsm.update(0.016)
    fsm.update(0.016)
    assert count[0] == 2


def test_invalid_state_raises():
    fsm = FSM()
    fsm.add_state(State("valid"))
    try:
        fsm.set_state("nonexistent")
        assert False
    except ValueError:
        pass


if __name__ == "__main__":
    test_state_transitions()
    test_state_update()
    test_invalid_state_raises()
    print("All FSM tests passed!")
