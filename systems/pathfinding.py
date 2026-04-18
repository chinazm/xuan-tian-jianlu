"""BFS 路径规划（网格化）。"""
from collections import deque
from core.vector import Vector2


def bfs_path(start: Vector2, end: Vector2, grid: list[list[int]], tile_size: int = 32, max_steps: int = 200) -> list[Vector2]:
    start_col, start_row = int(start.x // tile_size), int(start.y // tile_size)
    end_col, end_row = int(end.x // tile_size), int(end.y // tile_size)
    rows = len(grid)
    if rows == 0:
        return []
    cols = len(grid[0])

    if not (0 <= start_row < rows and 0 <= start_col < cols):
        return []
    if not (0 <= end_row < rows and 0 <= end_col < cols):
        return []

    queue = deque([(start_col, start_row, [])])
    visited = {(start_col, start_row)}
    directions = [(0,1),(0,-1),(1,0),(-1,0)]

    while queue:
        col, row, path = queue.popleft()
        if col == end_col and row == end_row:
            return [Vector2(c * tile_size + tile_size//2, r * tile_size + tile_size//2) for c, r in path]
        if len(path) >= max_steps:
            continue
        for dc, dr in directions:
            nc, nr = col + dc, row + dr
            if 0 <= nc < cols and 0 <= nr < rows and (nc, nr) not in visited and grid[nr][nc] == 0:
                visited.add((nc, nr))
                queue.append((nc, nr, path + [(nc, nr)]))
    return []
