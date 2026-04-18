"""对话系统：解析对话JSON、分支选择、条件判定。"""
import json
from pathlib import Path
from typing import Optional


class DialogueSystem:
    def __init__(self, data_path: str = "data/dialogues.json"):
        self._dialogues: dict = {}
        self._active: Optional[dict] = None
        self._current_line_index: int = 0
        p = Path(data_path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                self._dialogues = json.load(f)

    def start(self, dialogue_id: str) -> bool:
        if dialogue_id in self._dialogues:
            self._active = self._dialogues[dialogue_id]
            self._current_line_index = 0
            # Auto-advance to first line with choices or end
            self._skip_to_interaction()
            return True
        return False

    def _skip_to_interaction(self) -> None:
        """Auto-advance past non-interactive lines to the first one with choices."""
        lines = self._active.get("lines", [])
        while self._current_line_index < len(lines):
            line = lines[self._current_line_index]
            if line.get("choices"):
                return
            # If this is the last line, stop
            if self._current_line_index >= len(lines) - 1:
                return
            self._current_line_index += 1

    def current_line(self) -> Optional[dict]:
        if not self._active:
            return None
        lines = self._active.get("lines", [])
        if self._current_line_index < len(lines):
            return lines[self._current_line_index]
        return None

    def next(self, choice_index: int = 0) -> Optional[str]:
        if not self._active:
            return None
        line = self.current_line()
        if not line:
            return None

        choices = line.get("choices", [])
        if choices and choice_index < len(choices):
            choice = choices[choice_index]
            next_id = choice.get("next")
            if next_id and next_id in self._dialogues:
                self._active = self._dialogues[next_id]
                self._current_line_index = 0
                return next_id
        else:
            next_id = line.get("next")
            if next_id and next_id in self._dialogues:
                self._active = self._dialogues[next_id]
                self._current_line_index = 0
                return next_id

        self._active = None
        return None

    def has_choices(self) -> bool:
        line = self.current_line()
        return line is not None and bool(line.get("choices", []))

    def get_choices(self) -> list[dict]:
        line = self.current_line()
        return line.get("choices", []) if line else []

    def is_active(self) -> bool:
        return self._active is not None

    def end(self) -> None:
        self._active = None
        self._current_line_index = 0
