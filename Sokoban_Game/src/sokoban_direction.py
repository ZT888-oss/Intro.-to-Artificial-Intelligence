from typing import Tuple


class _SokobanDirection:
    """
    Represents a movement direction in the Sokoban grid.
    Each direction is defined by its delta (dx, dy).
    """
    def __init__(self, name: str, dx: int, dy: int):
        self.name = name
        self.dx = dx
        self.dy = dy

    def move(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Returns the position resulting from moving in this direction."""
        return (pos[0] + self.dx, pos[1] + self.dy)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

UP = _SokobanDirection("UP", 0, -1)
DOWN = _SokobanDirection("DOWN", 0, 1)
LEFT = _SokobanDirection("LEFT", -1, 0)
RIGHT = _SokobanDirection("RIGHT", 1, 0)
