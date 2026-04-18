"""资源懒加载管理器：LRU 缓存 + 按需加载。"""
import pygame
from pathlib import Path
from collections import OrderedDict
from typing import Optional


class ResourceManager:
    def __init__(self, max_cache_size: int = 100, base_path: str = "assets"):
        self._cache: OrderedDict[str, pygame.Surface] = OrderedDict()
        self._max_size = max_cache_size
        self._base_path = Path(base_path)

    def load(self, relative_path: str) -> pygame.Surface:
        """加载图片（懒加载 + LRU 缓存）。"""
        if relative_path in self._cache:
            self._cache.move_to_end(relative_path)
            return self._cache[relative_path]

        full_path = self._base_path / relative_path
        if not full_path.exists():
            raise FileNotFoundError(f"Resource not found: {full_path}")

        surface = pygame.image.load(str(full_path)).convert_alpha()

        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)

        self._cache[relative_path] = surface
        return surface

    def load_spritesheet(
        self, relative_path: str, tile_w: int = 32, tile_h: int = 32
    ) -> list[pygame.Surface]:
        """加载精灵表并切分为帧列表。"""
        sheet = self.load(relative_path)
        frames = []
        cols = sheet.get_width() // tile_w
        rows = sheet.get_height() // tile_h

        for row in range(rows):
            for col in range(cols):
                rect = pygame.Rect(col * tile_w, row * tile_h, tile_w, tile_h)
                frames.append(sheet.subsurface(rect))

        return frames

    def preload_paths(self, paths: list[str]) -> None:
        """预加载指定路径的资源。"""
        for path in paths:
            try:
                self.load(path)
            except FileNotFoundError:
                pass

    def cache_info(self) -> dict:
        return {
            "cached": len(self._cache),
            "max_size": self._max_size,
        }

    def clear(self) -> None:
        self._cache.clear()
