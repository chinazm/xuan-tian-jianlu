"""玩家实体：处理输入、移动、攻击。"""
import pygame
from .entity import Entity
from core.vector import Vector2
from core.input_handler import InputHandler
from core.config import PhysicsConfig, CombatConfig


class Player(Entity):
    def __init__(self, entity_id: str = "player", pos: Vector2 = None):
        pos = pos or Vector2(0, 0)
        super().__init__(entity_id=entity_id, pos=pos, size=Vector2(32, 32))
        self.attack_timer: float = 0.0
        self.dodge_timer: float = 0.0
        self.dodge_cooldown: float = 0.0
        self.invincible: bool = False
        self.invincible_timer: float = 0.0
        self._physics = PhysicsConfig()
        self._combat = CombatConfig()
        self.state: str = "idle"

    def handle_input(self, inp: InputHandler, dt: float) -> None:
        if not self.is_alive:
            return
        self.attack_timer = max(0, self.attack_timer - dt)
        self.dodge_cooldown = max(0, self.dodge_cooldown - dt)
        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

        if inp.consume_action("dodge") and self.dodge_cooldown <= 0:
            direction = inp.direction.normalized() if inp.is_direction_held() else self._get_facing_vector()
            self._dodge(direction)
            return
        if inp.consume_action("attack") and self.attack_timer <= 0:
            self._start_attack()
            return

        if inp.is_direction_held():
            move_dir = inp.direction.normalized()
            self.vel = move_dir * self.base_speed
            self.facing = self._vector_to_facing(move_dir)
            self.state = "walk"
        else:
            self.vel = Vector2(0, 0)
            self.state = "idle"

    def _start_attack(self) -> None:
        self.attack_timer = self._combat.default_attack_cooldown
        self.state = "attack"

    def _dodge(self, direction: Vector2) -> None:
        self.dodge_cooldown = self._physics.dodge_cooldown
        self.invincible = True
        self.invincible_timer = self._physics.dodge_duration
        self.vel = direction * (self._physics.dodge_distance / self._physics.dodge_duration)
        self.state = "dodge"
        self._dodge_elapsed = 0.0

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.state == "dodge":
            self._dodge_elapsed = getattr(self, "_dodge_elapsed", 0.0) + dt
            if self._dodge_elapsed >= self._physics.dodge_duration:
                self.state = "idle"
                if not self.is_knockback:
                    self.vel = Vector2(0, 0)
        elif self.state == "attack":
            if self.attack_timer <= 0:
                self.state = "idle"

    def get_attack_rect(self) -> pygame.Rect:
        facing_rects = {
            "up": (-8, -40, 48, 40),
            "down": (-8, 32, 48, 40),
            "left": (-40, -8, 40, 48),
            "right": (32, -8, 40, 48),
        }
        rx, ry, rw, rh = facing_rects.get(self.facing, (-8, 32, 48, 40))
        return pygame.Rect(int(self.pos.x + rx), int(self.pos.y + ry), rw, rh)

    def _get_facing_vector(self) -> Vector2:
        return {"up": Vector2(0,-1), "down": Vector2(0,1), "left": Vector2(-1,0), "right": Vector2(1,0)}.get(self.facing, Vector2(0,1))

    def _vector_to_facing(self, v: Vector2) -> str:
        if abs(v.x) > abs(v.y):
            return "right" if v.x > 0 else "left"
        return "down" if v.y > 0 else "up"

    def render(self, screen: pygame.Surface, camera) -> None:
        if self.invincible:
            import time
            if int(time.time() * 10) % 2 == 0:
                return
        super().render(screen, camera)
