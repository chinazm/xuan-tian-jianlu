"""输入处理系统：键盘 + 触屏双输入融合。"""
from dataclasses import dataclass, field
from typing import Optional
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
    
    # 触屏控制器引用（可选）
    _touch_controller: Optional[object] = field(default=None, repr=False)
    
    def set_touch_controller(self, controller) -> None:
        """设置触屏控制器。"""
        self._touch_controller = controller

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        current_pressed = set()

        # 1. 键盘方向输入
        kb_dx, kb_dy = 0, 0
        for keycode, action in self.key_map.items():
            is_down = keys[keycode]
            if is_down:
                current_pressed.add(keycode)

            if action in ("up", "down", "left", "right"):
                if is_down:
                    if action == "up":
                        kb_dy = -1
                    elif action == "down":
                        kb_dy = 1
                    elif action == "left":
                        kb_dx = -1
                    elif action == "right":
                        kb_dx = 1

        if kb_dx != 0 and kb_dy != 0:
            length = (kb_dx * kb_dx + kb_dy * kb_dy) ** 0.5
            kb_dx /= length
            kb_dy /= length

        kb_direction = Vector2(kb_dx, kb_dy)

        # 2. 触屏方向输入（优先于键盘）
        touch_direction = Vector2(0, 0)
        if self._touch_controller and self._touch_controller.direction.length() > 0:
            touch_direction = self._touch_controller.direction

        # 融合：触屏优先，无触屏时用键盘
        if touch_direction.length() > 0:
            self.direction = touch_direction
        else:
            self.direction = kb_direction

        # 3. 键盘动作键缓冲
        self._key_just_pressed.clear()
        for keycode, action in self.key_map.items():
            if action not in ("up", "down", "left", "right"):
                was_down = keycode in self._prev_key_state
                is_down = keys[keycode]
                if is_down and not was_down:
                    self._key_just_pressed[action] = True
                    if len(self.action_buffer) < self.buffer_max:
                        self.action_buffer.append(action)

        # 4. 触屏动作键融合
        if self._touch_controller:
            for action in ["attack", "skill", "dodge", "interact"]:
                if self._touch_controller.consume_action(action):
                    if action not in self._key_just_pressed:
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
