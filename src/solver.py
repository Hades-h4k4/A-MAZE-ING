"""Breadth-First Search maze solving sub-module."""

from typing import Dict, List, Set, Tuple

NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8

MOVE: Dict[int, Tuple[int, int]] = {
    NORTH: (-1, 0), EAST: (0, 1), SOUTH: (1, 0), WEST: (0, -1)
}


def solve_maze(grid: List[List[int]], entry: Tuple[int, int], exit_c: Tuple[int, int]) -> List[str]:
    """Finds the shortest route using a queue-based BFS algorithm."""
    queue: List[List[Tuple[int, int]]] = [[entry]]
    visited: Set[Tuple[int, int]] = {entry}
    dir_letters: Dict[int, str] = {NORTH: "N", EAST: "E", SOUTH: "S", WEST: "W"}
    height = len(grid)
    width = len(grid[0])

    while queue:
        path: List[Tuple[int, int]] = queue.pop(0)
        curr_r, curr_c = path[-1]

        if (curr_r, curr_c) == exit_c:
            letters: List[str] = []
            for i in range(len(path) - 1):
                r1, c1 = path[i]
                r2, c2 = path[i + 1]
                for d, (dr, dc) in MOVE.items():
                    if r1 + dr == r2 and c1 + dc == c2:
                        letters.append(dir_letters[d])
            return letters

        curr_walls: int = grid[curr_r][curr_c]
        for direction, (dr, dc) in MOVE.items():
            if not (curr_walls & direction):
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < height and 0 <= nc < width:
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append(path + [(nr, nc)])
    return []
