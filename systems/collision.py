"""AABB 碰撞检测 + 碰撞层系统。"""
import pygame
from core.vector import Vector2
from entities.entity import Entity


class CollisionSystem:
    def __init__(self):
        self._terrain_rects: list[pygame.Rect] = []
        self._entities: dict[str, Entity] = {}

    def set_terrain(self, rects: list[pygame.Rect]) -> None:
        self._terrain_rects = rects

    def add_entity(self, entity: Entity) -> None:
        self._entities[entity.entity_id] = entity

    def remove_entity(self, entity_id: str) -> None:
        self._entities.pop(entity_id, None)

    def check_terrain_collision(self, rect: pygame.Rect) -> bool:
        for terrain_rect in self._terrain_rects:
            if rect.colliderect(terrain_rect):
                return True
        return False

    def resolve_terrain(self, entity: Entity) -> Vector2:
        rect = entity.get_collision_rect()
        for terrain_rect in self._terrain_rects:
            if not rect.colliderect(terrain_rect):
                continue
            overlap_x = min(rect.right - terrain_rect.left, terrain_rect.right - rect.left)
            overlap_y = min(rect.bottom - terrain_rect.top, terrain_rect.bottom - rect.top)
            if overlap_x < overlap_y:
                if rect.centerx < terrain_rect.centerx:
                    entity.pos.x -= overlap_x
                else:
                    entity.pos.x += overlap_x
            else:
                if rect.centery < terrain_rect.centery:
                    entity.pos.y -= overlap_y
                else:
                    entity.pos.y += overlap_y
        return entity.pos

    def check_entity_collision(self, a: Entity, b: Entity) -> bool:
        return a.get_collision_rect().colliderect(b.get_collision_rect())

    def get_nearby_entities(self, pos: Vector2, radius: float) -> list[Entity]:
        result = []
        radius_sq = radius * radius
        for entity in self._entities.values():
            if not entity.is_alive:
                continue
            if (entity.pos - pos).length_squared() <= radius_sq:
                result.append(entity)
        return result

    def get_entities_in_rect(self, rect: pygame.Rect) -> list[Entity]:
        result = []
        for entity in self._entities.values():
            if not entity.is_alive:
                continue
            if entity.get_collision_rect().colliderect(rect):
                result.append(entity)
        return result
