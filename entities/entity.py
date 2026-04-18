"""通用实体基类。不绑定任何游戏内容，纯数据驱动。"""
from dataclasses import dataclass, field
from typing import Optional
import pygame
from core.vector import Vector2
from core.event_bus import EventBus


@dataclass
class Entity:
    entity_id: str
    pos: Vector2
    size: Vector2 = field(default_factory=lambda: Vector2(32, 32))
    vel: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    facing: str = "down"

    max_hp: float = 100.0
    current_hp: float = 100.0
    base_speed: float = 100.0

    sprite: Optional[pygame.Surface] = None
    animation_frames: list = field(default_factory=list)
    current_frame: int = 0
    frame_timer: float = 0.0
    frame_duration: float = 0.15

    is_alive: bool = True
    is_knockback: bool = False
    knockback_timer: float = 0.0

    def update(self, dt: float) -> None:
        if not self.is_alive:
            return
        if self.is_knockback:
            self.knockback_timer -= dt
            if self.knockback_timer <= 0:
                self.is_knockback = False
                self.vel = Vector2(0, 0)
        self.pos = self.pos + self.vel * dt

    def take_damage(self, amount: float, source_pos: Vector2, knockback_force: float = 80.0) -> None:
        self.current_hp = max(0, self.current_hp - amount)
        direction = (self.pos - source_pos).normalized()
        if direction.length() == 0:
            direction = Vector2(0, -1)
        self.vel = direction * knockback_force
        self.is_knockback = True
        self.knockback_timer = 0.15
        EventBus.publish("entity_hit", {"entity": self, "damage": amount, "source_pos": source_pos})
        if self.current_hp <= 0:
            self.is_alive = False
            EventBus.publish("entity_die", {"entity": self, "killer_pos": source_pos})

    def heal(self, amount: float) -> None:
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.pos.x), int(self.pos.y), int(self.size.x), int(self.size.y))

    def render(self, screen: pygame.Surface, camera) -> None:
        if not self.sprite:
            return
        if not camera.is_visible(self.pos, self.size):
            return
        screen_pos = camera.apply(self.pos)
        screen.blit(self.sprite, (int(screen_pos.x), int(screen_pos.y)))

    def animate(self, dt: float) -> None:
        if len(self.animation_frames) <= 1:
            return
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0.0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.sprite = self.animation_frames[self.current_frame]
