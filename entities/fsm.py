"""轻量级有限状态机。"""
from typing import Callable, Optional, Any


class State:
    def __init__(self, name: str, on_enter: Optional[Callable] = None,
                 on_update: Optional[Callable] = None, on_exit: Optional[Callable] = None):
        self.name = name
        self.on_enter = on_enter
        self.on_update = on_update
        self.on_exit = on_exit


class FSM:
    def __init__(self):
        self._states: dict[str, State] = {}
        self._current: Optional[State] = None
        self._params: dict[str, Any] = {}

    def add_state(self, state: State) -> None:
        self._states[state.name] = state

    def set_state(self, name: str, params: dict = None) -> None:
        if name not in self._states:
            raise ValueError(f"State not found: {name}")
        if self._current and self._current.on_exit:
            self._current.on_exit()
        self._current = self._states[name]
        self._params = params or {}
        if self._current.on_enter:
            self._current.on_enter(self._params)

    def update(self, dt: float) -> None:
        if self._current and self._current.on_update:
            self._current.on_update(dt, self._params)

    @property
    def current_state(self) -> Optional[str]:
        return self._current.name if self._current else None
