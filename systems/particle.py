"""粒子特效系统。"""
import pygame
import random
from core.vector import Vector2
from dataclasses import dataclass


@dataclass
class Particle:
    pos: Vector2
    vel: Vector2
    lifetime: float
    max_lifetime: float
    color: tuple
    size: int


class ParticleSystem:
    def __init__(self):
        self._particles: list[Particle] = []

    def emit(self, pos: Vector2, count: int, color: tuple, speed: float = 50, lifetime: float = 0.5, size: int = 3):
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            vel = Vector2(random.uniform(-speed, speed), random.uniform(-speed, speed))
            self._particles.append(Particle(
                pos=Vector2(pos.x, pos.y),
                vel=vel,
                lifetime=lifetime,
                max_lifetime=lifetime,
                color=color,
                size=size,
            ))

    def update(self, dt: float):
        for p in self._particles:
            p.pos += p.vel * dt
            p.lifetime -= dt
        self._particles = [p for p in self._particles if p.lifetime > 0]

    def render(self, screen: pygame.Surface, camera):
        for p in self._particles:
            alpha = int((p.lifetime / p.max_lifetime) * 255)
            pos = camera.apply(p.pos)
            surf = pygame.Surface((p.size, p.size), pygame.SRCALPHA)
            surf.fill((*p.color, alpha))
            screen.blit(surf, (int(pos.x), int(pos.y)))
