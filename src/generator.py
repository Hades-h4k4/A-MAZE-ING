"""Iterative DFS maze generation core module."""
# Depth-First Search (Busqueda profunda)
import random
from typing import Dict, Any, List, Set, Tuple, Optional
from src.solver import solve_maze


# Type hint alias
Grid = List[List[int]]
# Type hint alias
MatrixBool = List[List[bool]]

# Bitwise mask
NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8

# A dictionary mapping each directional bitmask value to its logical inverse
OPPOSITE: Dict[int, int] = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
# A dictionary mapping directional masks to physical coordinate offsets
MOVE: Dict[int, Tuple[int, int]] = {
    NORTH: (-1, 0), EAST: (0, 1), SOUTH: (1, 0), WEST: (0, -1)
}


class MazeGenerator:
    """Standalone reusable maze generator engine class."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.width: int = int(config["WIDTH"])
        self.height: int = int(config["HEIGHT"])

        c_entry: Tuple[int, int] = config["ENTRY"]
        c_exit: Tuple[int, int] = config["EXIT"]
        self.entry: Tuple[int, int] = (c_entry[1], c_entry[0])
        self.exit: Tuple[int, int] = (c_exit[1], c_exit[0])
        self.output_file: str = str(config["OUTPUT_FILE"])
        self.perfect: bool = bool(config["PERFECT"])
        self.display_mode: str = str(config.get("DISPLAY_MODE", "ascii"))

        # Seed checker
        seed_val: Optional[int] = config.get("SEED")
        self.seed: int = seed_val or random.randint(0, 100000)
        # save the seed to ramdon for make it reproductible
        random.seed(self.seed)

        # inicialize the grid.
        self.grid: Grid = [[15] * self.width for _ in range(self.height)]
        self.path_solution: List[str] = []

        # fixed minimun space for the 42 pattern
        self.p_rows: int = 5
        self.p_cols: int = 9
        # Hardcode pattern
        self.pattern: List[List[int]] = [
            [1, 0, 0, 1, 0, 1, 1, 1, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 1, 1, 1, 1],
            [0, 0, 0, 1, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 1, 1, 1, 1]
        ]

    def generate(self) -> None:
        """Carves paths matching constraints and cell coherence."""
        # check if it fit 42 pattern
        has_42: bool = (
            self.height >= self.p_rows + 2 and self.width >= self.p_cols + 2
        )
        # Close cells for the maze
        closed_cells: Set[Tuple[int, int]] = set()

        if has_42:
            # were will begin the logo
            start_r: int = (self.height - self.p_rows) // 2
            start_c: int = (self.width - self.p_cols) // 2
            # Iterates de logo in the maze
            for r in range(self.p_rows):
                for c in range(self.p_cols):
                    # Checks if wall or solid
                    if self.pattern[r][c] == 1:
                        grid_r, grid_c = start_r + r, start_c + c
                        self.grid[grid_r][grid_c] = 15
                        # Adds this absolute position to the pre-filled cells
                        closed_cells.add((grid_r, grid_c))

                        # this loop check every wall around 42 logo is closed
                        for direction, (dr, dc) in MOVE.items():
                            nr, nc = grid_r + dr, grid_c + dc
                            if 0 <= nr < self.height and 0 <= nc < self.width:
                                self.grid[nr][nc] |= OPPOSITE[direction]
        else:
            print("⚠️ Warning: Maze size too small for '42' pattern.")

        # define if the cell is walkable or not.
        visite: MatrixBool = [[False] * self.width for _ in range(self.height)]
        for r, c in closed_cells:
            # Clossing cells turn into True, so no walkable
            visite[r][c] = True

        # Initializes the DFS backtracking stack array
        stack: List[Tuple[int, int]] = [self.entry]
        # Marks the starting maze entrance cell as visited to prevent loop back
        visite[self.entry[0]][self.entry[1]] = True

        # while stack no full still going
        while stack:
            curr_r, curr_c = stack[-1]
            # check if cell could be clear
            neighbors: List[Tuple[int, int, int]] = []
            for direction, (dr, dc) in MOVE.items():
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    if not visite[nr][nc]:
                        neighbors.append((direction, nr, nc))

            # create gabs size controled
            if neighbors:
                direction, nr, nc = random.choice(neighbors)
                if self.would_crte_3x3_open_spc(curr_r, curr_c, direction):
                    visite[nr][nc] = True
                    continue

                if direction == NORTH:
                    self.grid[curr_r][curr_c] = self.grid[curr_r][curr_c] - 1
                elif direction == EAST:
                    self.grid[curr_r][curr_c] = self.grid[curr_r][curr_c] - 2
                elif direction == SOUTH:
                    self.grid[curr_r][curr_c] = self.grid[curr_r][curr_c] - 4
                elif direction == WEST:
                    self.grid[curr_r][curr_c] = self.grid[curr_r][curr_c] - 8

                if direction == NORTH:
                    self.grid[nr][nc] = self.grid[nr][nc] - 4
                elif direction == EAST:
                    self.grid[nr][nc] = self.grid[nr][nc] - 8
                elif direction == SOUTH:
                    self.grid[nr][nc] = self.grid[nr][nc] - 1
                elif direction == WEST:
                    self.grid[nr][nc] = self.grid[nr][nc] - 2

                visite[nr][nc] = True
                stack.append((nr, nc))
            else:
                stack.pop()

        for c in range(self.width):
            self.grid[0][c] |= NORTH
            self.grid[self.height - 1][c] |= SOUTH
        for r in range(self.height):
            self.grid[r][0] |= WEST
            self.grid[r][self.width - 1] |= EAST

    # Validates corridor widths constraint to avoid large open areas.
    def would_crte_3x3_open_spc(self, r: int, c: int, direction: int) -> bool:
        dr, dc = MOVE[direction]
        nr, nc = r + dr, c + dc

        orig_curr = self.grid[r][c]
        orig_neigh = self.grid[nr][nc]

        if direction == NORTH:
            self.grid[r][c] = self.grid[r][c] - 1
            self.grid[nr][nc] = self.grid[nr][nc] - 4
        elif direction == EAST:
            self.grid[r][c] = self.grid[r][c] - 2
            self.grid[nr][nc] = self.grid[nr][nc] - 8
        elif direction == SOUTH:
            self.grid[r][c] = self.grid[r][c] - 4
            self.grid[nr][nc] = self.grid[nr][nc] - 1
        elif direction == WEST:
            self.grid[r][c] = self.grid[r][c] - 8
            self.grid[nr][nc] = self.grid[nr][nc] - 2

        open_count: int = 0
        for i in range(max(0, r - 1), min(self.height, r + 2)):
            for j in range(max(0, c - 1), min(self.width, c + 2)):
                if self.grid[i][j] == 0:
                    open_count += 1

        self.grid[r][c] = orig_curr
        self.grid[nr][nc] = orig_neigh

        return open_count >= 4

    def solve(self) -> bool:
        self.path_solution = solve_maze(self.grid, self.entry, self.exit)
        return len(self.path_solution) > 0

    def display(self, show_solution: bool = False) -> None:
        # Renders the maze using terminal colors.
        from src.main import THEMES, COLOR_WALL, COLOR_RESET
        from src.main import COLOR_SE, COLOR_PATH, COLOR_NUM42
        style = THEMES.get(self.display_mode, THEMES["ascii"])
        sol_coords: Set[Tuple[int, int]] = set()

        if show_solution and self.path_solution:
            curr_r, curr_c = self.entry
            sol_coords.add((curr_r, curr_c))
            dir_map: Dict[str, int] = {
                "N": NORTH, "E": EAST, "S": SOUTH, "W": WEST}
            for move in self.path_solution:
                dr, dc = MOVE[dir_map[move]]
                curr_r, curr_c = curr_r + dr, curr_c + dc
                sol_coords.add((curr_r, curr_c))

        print(
            COLOR_WALL + style["corner"] +
            (style["h_wall"] + style["corner"]) *
            self.width + COLOR_RESET)
        for r in range(self.height):
            row_str = COLOR_WALL + style["v_wall"] + COLOR_RESET
            for c in range(self.width):
                if (r, c) == self.entry:
                    cell_char = f"{COLOR_SE} S {COLOR_RESET}"
                elif (r, c) == self.exit:
                    cell_char = f"{COLOR_SE} E {COLOR_RESET}"
                elif (r, c) in sol_coords:
                    cell_char = f"{COLOR_PATH}{style['path']}{COLOR_RESET}"
                elif self.grid[r][c] == 15:
                    cell_char = f"{COLOR_NUM42}{style['block42']}{COLOR_RESET}"
                else:
                    cell_char = "   "

                wall_east = (
                    f"{COLOR_WALL}{style['v_wall']}{COLOR_RESET}"
                    if (self.grid[r][c] & EAST) else style["v_open"])
                row_str += cell_char + wall_east
            print(row_str)

            bottom_str = COLOR_WALL + style["corner"] + COLOR_RESET
            for c in range(self.width):
                wall_south = (
                    f"{COLOR_WALL}{style['h_wall']}{COLOR_RESET}"
                    if (self.grid[r][c] & SOUTH) else style["h_open"]
                    )
                bottom_str += (
                    wall_south + f"{COLOR_WALL}{style['corner']}{COLOR_RESET}")
            print(bottom_str)

    def save_to_file(self) -> None:
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                for r in range(self.height):
                    hex_row = (
                        "".join([hex(self.grid[r][c])[2:].upper()
                                 for c in range(self.width)]))
                    f.write(hex_row + "\n")
                f.write("\n")
                f.write(f"{self.entry[1]},{self.entry[0]}\n")
                f.write(f"{self.exit[1]},{self.exit[0]}\n")
                f.write("".join(self.path_solution) + "\n")
        except IOError as err:
            print(f"❌ Error writing to output file: {err}")
