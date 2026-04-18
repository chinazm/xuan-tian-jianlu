"""Vector2 单元测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.vector import Vector2


def test_add():
    a = Vector2(1, 2)
    b = Vector2(3, 4)
    result = a + b
    assert result.x == 4
    assert result.y == 6


def test_sub():
    a = Vector2(5, 5)
    b = Vector2(2, 3)
    result = a - b
    assert result.x == 3
    assert result.y == 2


def test_mul():
    v = Vector2(2, 3)
    result = v * 3
    assert result.x == 6
    assert result.y == 9
    # rmul
    result2 = 3 * v
    assert result2.x == 6


def test_length():
    v = Vector2(3, 4)
    assert v.length() == 5.0


def test_length_squared():
    v = Vector2(3, 4)
    assert v.length_squared() == 25.0


def test_normalized():
    v = Vector2(3, 4)
    n = v.normalized()
    assert abs(n.length() - 1.0) < 0.0001


def test_normalized_zero():
    v = Vector2(0, 0)
    n = v.normalized()
    assert n.x == 0
    assert n.y == 0


def test_distance_to():
    a = Vector2(0, 0)
    b = Vector2(3, 4)
    assert a.distance_to(b) == 5.0


def test_dot():
    a = Vector2(1, 0)
    b = Vector2(0, 1)
    assert a.dot(b) == 0


def test_tuple():
    v = Vector2(1.5, 2.5)
    assert v.tuple() == (1.5, 2.5)


if __name__ == "__main__":
    test_add()
    test_sub()
    test_mul()
    test_length()
    test_length_squared()
    test_normalized()
    test_normalized_zero()
    test_distance_to()
    test_dot()
    test_tuple()
    print("All vector tests passed!")
