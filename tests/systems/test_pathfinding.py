import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from systems.pathfinding import bfs_path
from core.vector import Vector2


def test_bfs_simple_path():
    grid = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    path = bfs_path(Vector2(0, 0), Vector2(64, 64), grid, tile_size=32)
    assert len(path) > 0


def test_bfs_blocked():
    grid = [
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
    ]
    path = bfs_path(Vector2(0, 0), Vector2(64, 64), grid, tile_size=32)
    assert len(path) == 0


if __name__ == "__main__":
    test_bfs_simple_path()
    test_bfs_blocked()
    print("All pathfinding tests passed!")
