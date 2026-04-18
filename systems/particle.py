"""粒子特效系统 (优化版：Surface 缓存)。"""
import pygame
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
    alpha: int


# 全局 Surface 缓存
_surface_cache: dict = {}
MAX_CACHE_SIZE = 50


def get_particle_surface(size: int, color: tuple, alpha: int) -> pygame.Surface:
    """获取或创建指定参数的粒子 Surface（带缓存）。"""
    cache_key = (size, color, alpha)
    if cache_key in _surface_cache:
        return _surface_cache[cache_key]
    
    # LRU 策略：如果缓存满了，清理掉一半
    if len(_surface_cache) >= MAX_CACHE_SIZE:
        keys_to_remove = list(_surface_cache.keys())[:MAX_CACHE_SIZE // 2]
        for k in keys_to_remove:
            del _surface_cache[k]
    
    # 创建新 Surface
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((*color, alpha))
    _surface_cache[cache_key] = surf
    return surf


class ParticleSystem:
    def __init__(self, max_particles: int = 500):
        self._particles: list[Particle] = []
        self.max_particles = max_particles

    def emit(self, pos: Vector2, count: int, color: tuple, speed: float = 50, lifetime: float = 0.5, size: int = 3, alpha: int = 255):
        """发射粒子。"""
        import random
        for _ in range(count):
            if len(self._particles) >= self.max_particles:
                # 移除最老的
                self._particles.pop(0)
                
            vel = Vector2(random.uniform(-speed, speed), random.uniform(-speed, speed))
            self._particles.append(Particle(
                pos=Vector2(pos.x, pos.y),
                vel=vel,
                lifetime=lifetime,
                max_lifetime=lifetime,
                color=color,
                size=size,
                alpha=alpha,
            ))

    def update(self, dt: float):
        """更新粒子状态。"""
        for p in self._particles:
            p.pos += p.vel * dt
            p.lifetime -= dt
        self._particles = [p for p in self._particles if p.lifetime > 0]

    def render(self, screen: pygame.Surface, camera):
        """批量渲染粒子。"""
        for p in self._particles:
            # 计算当前透明度 (随生命周期衰减)
            current_alpha = int((p.lifetime / p.max_lifetime) * p.alpha)
            pos = camera.apply(p.pos)
            
            # 复用缓存的 Surface
            surf = get_particle_surface(p.size, p.color, current_alpha)
            screen.blit(surf, (int(pos.x), int(pos.y)))
