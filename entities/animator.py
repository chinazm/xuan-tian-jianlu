"""动画控制器：管理精灵帧序列播放。"""
import pygame
from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class Animation:
    name: str
    frames: list[pygame.Surface]
    frame_duration: float = 0.15
    loop: bool = True
    on_complete: Optional[Callable] = None


class Animator:
    def __init__(self):
        self._animations: dict[str, Animation] = {}
        self._current: Optional[Animation] = None
        self._frame_index: int = 0
        self._timer: float = 0.0
        self._finished: bool = False

    def add(self, animation: Animation) -> None:
        self._animations[animation.name] = animation

    def play(self, name: str) -> None:
        if self._current and self._current.name == name:
            return
        if name not in self._animations:
            return
        self._current = self._animations[name]
        self._frame_index = 0
        self._timer = 0.0
        self._finished = False

    def update(self, dt: float) -> None:
        if not self._current or self._finished:
            return
        self._timer += dt
        if self._timer >= self._current.frame_duration:
            self._timer = 0.0
            self._frame_index += 1
            if self._frame_index >= len(self._current.frames):
                if self._current.loop:
                    self._frame_index = 0
                else:
                    self._frame_index = len(self._current.frames) - 1
                    self._finished = True
                    if self._current.on_complete:
                        self._current.on_complete()

    @property
    def current_frame(self) -> Optional[pygame.Surface]:
        if self._current and self._current.frames:
            return self._current.frames[self._frame_index]
        return None

    @property
    def is_finished(self) -> bool:
        return self._finished

    def reset(self) -> None:
        self._current = None
        self._finished = True
