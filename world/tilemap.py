"""Tilemap 渲染：从 JSON 加载地图，按 Tile 渲染，支持视锥裁剪。"""
import json
import pygame
from pathlib import Path
from core.vector import Vector2
from core.resource_manager import ResourceManager


class Tilemap:
    def __init__(self, resource_mgr: ResourceManager, tile_size: int = 32):
        self._resource_mgr = resource_mgr
        self._tile_size = tile_size
        self._tiles: list[list[int]] = []
        self._width = 0
        self._height = 0
        self._tileset: pygame.Surface | None = None
        self._collision_tiles: set[int] = set()
        self._tileset_width = 0

    def load(self, map_path: str, tileset_path: str, collision_tile_ids: list[int] = None) -> None:
        path = Path(map_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._tiles = data.get("tiles", [])
        self._width = len(self._tiles[0]) if self._tiles else 0
        self._height = len(self._tiles)
        self._collision_tiles = set(collision_tile_ids or [])

        if tileset_path:
            self._tileset = self._resource_mgr.load(tileset_path)
            self._tileset_width = self._tileset.get_width() // self._tile_size

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def pixel_width(self) -> int:
        return self._width * self._tile_size

    @property
    def pixel_height(self) -> int:
        return self._height * self._tile_size

    def get_tile(self, col: int, row: int) -> int:
        if 0 <= row < self._height and 0 <= col < self._width:
            return self._tiles[row][col]
        return 0

    def is_collision_tile(self, tile_id: int) -> bool:
        return tile_id in self._collision_tiles

    def render(self, screen: pygame.Surface, camera) -> None:
        if not self._tileset:
            return

        view_x, view_y, view_x2, view_y2 = camera.world_rect()
        start_col = max(0, view_x // self._tile_size - 1)
        start_row = max(0, view_y // self._tile_size - 1)
        end_col = min(self._width, view_x2 // self._tile_size + 2)
        end_row = min(self._height, view_y2 // self._tile_size + 2)

        tile_cols = self._tileset_width

        # 计算相机偏移
        cam_x = int(camera.pos.x)
        cam_y = int(camera.pos.y)

        for row in range(start_row, end_row):
            # 预计算 Y
            screen_y = row * self._tile_size - cam_y
            
            # 获取行数据
            row_data = self._tiles[row]
            
            for col in range(start_col, end_col):
                tile_id = row_data[col]
                if tile_id == 0:
                    continue

                # 计算 Source Rect
                tile_id -= 1  # 0-indexed
                src_x = (tile_id % tile_cols) * self._tile_size
                src_y = (tile_id // tile_cols) * self._tile_size
                src_rect = (src_x, src_y, self._tile_size, self._tile_size)

                # 计算 Dest Pos
                screen_x = col * self._tile_size - cam_x
                
                screen.blit(self._tileset, (screen_x, screen_y), src_rect)

    def get_collision_rects(self) -> list[pygame.Rect]:
        rects = []
        ts = self._tile_size
        for row in range(self._height):
            for col in range(self._width):
                if self.is_collision_tile(self._tiles[row][col]):
                    rects.append(pygame.Rect(col * ts, row * ts, ts, ts))
        return rects
