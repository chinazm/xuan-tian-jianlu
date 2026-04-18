"""敌人实体：巡逻/追击/攻击 AI。"""
import pygame
from .entity import Entity
from core.vector import Vector2
from core.config import CombatConfig
from collections import deque
import random


class Enemy(Entity):
    def __init__(self, entity_id: str, pos: Vector2, patrol_center: Vector2 = None, patrol_radius: float = 100.0):
        super().__init__(entity_id=entity_id, pos=pos, size=Vector2(32, 32))
        self.patrol_center = patrol_center or pos
        self.patrol_radius = patrol_radius
        self._combat = CombatConfig()
        self.attack_cooldown = 0.0
        self.state = "patrol"
        self.patrol_target = self._new_patrol_target()
        self.state_timer = 0.0

    def _new_patrol_target(self) -> Vector2:
        angle = random.uniform(0, 6.28)
        r = random.uniform(0, self.patrol_radius)
        return Vector2(
            self.patrol_center.x + r * __import__("math").cos(angle),
            self.patrol_center.y + r * __import__("math").sin(angle),
        )

    def update(self, dt: float) -> None:
        super().update(dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.state_timer += dt
        if not self.is_knockback:
            if self.state == "patrol":
                self._update_patrol(dt)
            elif self.state == "chase":
                self._update_chase(dt)

    def _update_patrol(self, dt: float) -> None:
        direction = (self.patrol_target - self.pos).normalized()
        if direction.length() > 0:
            self.vel = direction * self.base_speed * 0.3
            self.facing = "right" if direction.x > 0 else "left"
        if self.pos.distance_to(self.patrol_target) < 20:
            self.patrol_target = self._new_patrol_target()

    def _update_chase(self, dt: float) -> None:
        pass  # 由外部 AI 管理器控制

    def can_see_player(self, player_pos: Vector2, max_distance: float = 200.0) -> bool:
        return self.pos.distance_to(player_pos) <= max_distance

    def start_chase(self, target_pos: Vector2) -> None:
        self.state = "chase"
        direction = (target_pos - self.pos).normalized()
        self.vel = direction * self.base_speed
        self.facing = "right" if direction.x > 0 else "left"

    def stop_chase(self) -> None:
        self.state = "patrol"
        self.patrol_target = self._new_patrol_target()

    def render(self, screen: pygame.Surface, camera) -> None:
        if not self.sprite:
            pygame.draw.rect(screen, (200, 50, 50), (
                int(self.pos.x - camera.pos.x),
                int(self.pos.y - camera.pos.y),
                int(self.size.x), int(self.size.y)
            ))
            return
        super().render(screen, camera)

    def get_sprite_frame(self) -> int:
        """Get current animation frame (0-2)."""
        import time
        return int(time.time() * 4) % 3
