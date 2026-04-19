"""资源懒加载管理器：LRU 缓存 + 按需加载。"""
import pygame
import os
from pathlib import Path
from collections import OrderedDict
from typing import Optional


def get_base_dir() -> Path:
    """获取项目根目录，兼容桌面和 Android APK 环境。"""
    # 统一使用 __file__ 定位项目根目录（不依赖 os.getcwd()，
    # 因为 Android 上 cwd 可能指向错误的目录）
    return Path(os.path.dirname(os.path.abspath(__file__))).parent


class ResourceManager:
    def __init__(self, max_cache_size: int = 100, base_path: str = "assets", base_dir: Path = None):
        self._cache: OrderedDict[str, pygame.Surface] = OrderedDict()
        self._max_size = max_cache_size
        self._base_dir = base_dir or get_base_dir()
        self._base_path = self._base_dir / base_path

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


    def load_enemy_sprite(self, enemy_type: str) -> list:
        """Load 3-frame enemy animation sprite sheet."""
        path = f"sprites/enemy_{enemy_type}.png"
        try:
            return self.load_spritesheet(path, 32, 32)
        except FileNotFoundError:
            return None

    def load_npc_sprite(self, npc_id: str) -> list:
        """Load 4-direction × 4-frame NPC sprite sheet (128×128)."""
        path = f"sprites/npc_{npc_id}.png"
        try:
            return self.load_spritesheet(path, 32, 32)
        except FileNotFoundError:
            return None

    def load_item_sprite(self, item_id: str):
        """Load single item sprite."""
        path = f"items/{item_id}.png"
        try:
            return self.load(path)
        except FileNotFoundError:
            return None

    def cache_info(self) -> dict:
        return {
            "cached": len(self._cache),
            "max_size": self._max_size,
        }

    def clear(self) -> None:
        self._cache.clear()
