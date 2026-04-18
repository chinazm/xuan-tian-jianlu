"""战斗系统：处理攻击判定、伤害计算、投射物。"""
import pygame
from typing import Optional
from core.vector import Vector2
from core.event_bus import EventBus
from core.config import CombatConfig
from entities.entity import Entity


class Projectile(Entity):
    def __init__(self, pos: Vector2, direction: Vector2, damage: float, speed: float = 300, owner_id: str = ""):
        super().__init__(entity_id=f"projectile_{int(pos.x)}_{int(pos.y)}", pos=pos, size=Vector2(16, 16), max_hp=1, current_hp=1)
        self.vel = direction.normalized() * speed
        self.damage = damage
        self.lifetime = 2.0
        self.owner_id = owner_id

    def update(self, dt: float) -> None:
        super().update(dt)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.is_alive = False


class CombatSystem:
    def __init__(self):
        self._projectiles: list[Projectile] = []
        self._config = CombatConfig()

    def spawn_projectile(self, pos: Vector2, direction: Vector2, damage: float, owner_id: str = "") -> Projectile:
        proj = Projectile(pos, direction, damage, owner_id=owner_id)
        self._projectiles.append(proj)
        return proj

    def update(self, dt: float, targets: list[Entity]) -> list[dict]:
        hits = []
        for proj in self._projectiles:
            if not proj.is_alive:
                continue
            proj.update(dt)
            for target in targets:
                if not target.is_alive or target.entity_id == proj.owner_id:
                    continue
                if proj.get_collision_rect().colliderect(target.get_collision_rect()):
                    target.take_damage(proj.damage, proj.pos)
                    hits.append({"target": target, "damage": proj.damage})
                    proj.is_alive = False
                    break
        self._projectiles = [p for p in self._projectiles if p.is_alive]
        return hits

    def get_projectiles(self) -> list[Projectile]:
        return self._projectiles
