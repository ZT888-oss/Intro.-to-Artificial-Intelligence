from typing import List, Tuple, FrozenSet, Optional

from .state import StateSpace
from .sokoban_direction import UP, DOWN, LEFT, RIGHT


class SokobanState(StateSpace):
    """
    A class that represents a Sokoban state.
    """

    def __init__(
        self,
        action: Optional[str],
        gval: float,
        parent: Optional['SokobanState'],
        width: int,
        height: int,
        robots: Tuple[Tuple[int, int], ...],
        boxes: FrozenSet[Tuple[int, int]],
        storage: FrozenSet[Tuple[int, int]],
        obstacles: FrozenSet[Tuple[int, int]]
    ):
        """
        :param width: the room's X dimension (excluding walls).
        :param height: the room's Y dimension (excluding walls).
        :param robots: the locations of the robots, each of which is denoted by index.
        :param boxes: the locations of the boxes.
        :param storage: the locations of the storage points.
        :param obstacles: the locations of the impassable obstacles
        """
        StateSpace.__init__(self, action, gval, parent)
        self.width = width
        self.height = height
        self.robots = robots
        self.boxes = boxes
        self.storage = storage
        self.obstacles = obstacles

    def successors(self) -> List['SokobanState']:
        successors = []
        for robot_idx, robot_pos in enumerate(self.robots):
            for direction in (UP, RIGHT, DOWN, LEFT):
                new_pos = direction.move(robot_pos)

                if not self._in_bounds(new_pos) or new_pos in self.obstacles:
                    continue

                new_robots = list(self.robots)
                new_boxes = set(self.boxes)

                if new_pos in self.boxes:
                    box_dest = direction.move(new_pos)
                    if (
                        not self._in_bounds(box_dest)
                        or box_dest in self.obstacles
                        or box_dest in self.boxes
                    ):
                        continue
                    new_boxes.remove(new_pos)
                    new_boxes.add(box_dest)

                new_robots[robot_idx] = new_pos
                new_state = SokobanState(
                    action=f"Move robot {robot_idx} {direction}",
                    gval=self.gval + 1,
                    parent=self,
                    width=self.width,
                    height=self.height,
                    robots=tuple(new_robots),
                    boxes=frozenset(new_boxes),
                    storage=self.storage,
                    obstacles=self.obstacles
                )
                successors.append(new_state)
        return successors

    def hashable_state(self) -> int:
        return hash((self.robots, self.boxes))

    def state_string(self) -> str:
        map = []
        for y in range(0, self.height):
            row = []
            for x in range(0, self.width):
                row += [' ']
            map += [row]

        for storage_point in self.storage:
            map[storage_point[1]][storage_point[0]] = '.'
        for obstacle in self.obstacles:
            map[obstacle[1]][obstacle[0]] = '#'
        for i, robot in enumerate(self.robots):
            if robot in self.storage:
                map[robot[1]][robot[0]] = chr(ord('A') + i)
            else:
                map[robot[1]][robot[0]] = chr(ord('a') + i)
        for box in self.boxes:
            if box in self.storage:
                map[box[1]][box[0]] = '*'
            else:
                map[box[1]][box[0]] = '$'

        for y in range(0, self.height):
            map[y] = ['#'] + map[y]
            map[y] = map[y] + ['#']
        map = ['#' * (self.width + 2)] + map
        map = map + ['#' * (self.width + 2)]

        s = ''
        for row in map:
            for char in row:
                s += char
            s += '\n'

        return s

    def print_state(self) -> None:
        print("ACTION was " + self.action)
        print(self.state_string())

    def _in_bounds(self, loc: Tuple[int, int]) -> bool:
        x, y = loc
        return 0 <= x < self.width and 0 <= y < self.height

def sokoban_goal_state(state) -> bool:
    for box in state.boxes:
        if box not in state.storage:
            return False
    return True
