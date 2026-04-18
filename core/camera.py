"""摄像机系统：平滑跟随目标，限制在地图边界内。"""
from core.vector import Vector2


class Camera:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.pos = Vector2(0, 0)
        self.target = Vector2(0, 0)
        self.smoothing = 0.1
        self.map_bounds = None

    def set_bounds(self, map_width: int, map_height: int) -> None:
        self.map_bounds = (map_width, map_height)

    def follow(self, target_pos: Vector2, dt: float) -> None:
        self.target = Vector2(
            target_pos.x - self.width // 2,
            target_pos.y - self.height // 2,
        )
        self.pos.x += (self.target.x - self.pos.x) * self.smoothing
        self.pos.y += (self.target.y - self.pos.y) * self.smoothing

        if self.map_bounds:
            mw, mh = self.map_bounds
            self.pos.x = max(0, min(self.pos.x, mw - self.width))
            self.pos.y = max(0, min(self.pos.y, mh - self.height))

    def apply(self, pos: Vector2) -> Vector2:
        return Vector2(pos.x - self.pos.x, pos.y - self.pos.y)

    def is_visible(self, pos: Vector2, size: Vector2, margin: int = 64) -> bool:
        screen_pos = self.apply(pos)
        return not (
            screen_pos.x + size.x < -margin
            or screen_pos.x > self.width + margin
            or screen_pos.y + size.y < -margin
            or screen_pos.y > self.height + margin
        )

    def world_rect(self) -> tuple[int, int, int, int]:
        return (
            int(self.pos.x),
            int(self.pos.y),
            int(self.pos.x + self.width),
            int(self.pos.y + self.height),
        )
