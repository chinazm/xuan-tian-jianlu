"""输入处理系统：方向键实时响应 + 动作键缓冲队列。"""
from dataclasses import dataclass, field
import pygame
from core.vector import Vector2

DEFAULT_KEY_MAP = {
    pygame.K_w: "up",
    pygame.K_s: "down",
    pygame.K_a: "left",
    pygame.K_d: "right",
    pygame.K_j: "attack",
    pygame.K_k: "skill",
    pygame.K_l: "dodge",
    pygame.K_e: "interact",
    pygame.K_i: "inventory",
    pygame.K_c: "cultivate",
    pygame.K_r: "realm",
    pygame.K_m: "map",
    pygame.K_ESCAPE: "menu",
}


@dataclass
class InputHandler:
    key_map: dict = field(default_factory=lambda: dict(DEFAULT_KEY_MAP))
    direction: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    action_buffer: list = field(default_factory=list)
    buffer_max: int = 5

    _prev_key_state: set = field(default_factory=set, repr=False)
    _key_just_pressed: dict = field(default_factory=dict, repr=False)

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        current_pressed = set()

        dx, dy = 0, 0
        for keycode, action in self.key_map.items():
            is_down = keys[keycode]
            if is_down:
                current_pressed.add(keycode)

            if action in ("up", "down", "left", "right"):
                if is_down:
                    if action == "up":
                        dy = -1
                    elif action == "down":
                        dy = 1
                    elif action == "left":
                        dx = -1
                    elif action == "right":
                        dx = 1

        if dx != 0 and dy != 0:
            length = (dx * dx + dy * dy) ** 0.5
            dx /= length
            dy /= length

        self.direction = Vector2(dx, dy)

        self._key_just_pressed.clear()
        for keycode, action in self.key_map.items():
            if action not in ("up", "down", "left", "right"):
                was_down = keycode in self._prev_key_state
                is_down = keys[keycode]
                if is_down and not was_down:
                    self._key_just_pressed[action] = True
                    if len(self.action_buffer) < self.buffer_max:
                        self.action_buffer.append(action)

        self._prev_key_state = current_pressed

    def consume_action(self, action_name: str) -> bool:
        if action_name in self.action_buffer:
            self.action_buffer.remove(action_name)
            return True
        return False

    def is_action_just_pressed(self, action_name: str) -> bool:
        return self._key_just_pressed.get(action_name, False)

    def is_direction_held(self) -> bool:
        return self.direction.length() > 0
