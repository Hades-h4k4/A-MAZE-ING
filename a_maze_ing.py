"""Main entry point for the A-Maze-ing generator project.

Adheres strictly to Chapter IV parameters and validation requirements.
"""

import ast
import os
import random
import sys
from typing import Dict, Any, List, Set, Tuple, Optional

# --- WALL CONTROL BITS (IV.5 Requirements) ---
NORTH: int = 1  # Bit 0 (0001)
EAST: int = 2   # Bit 1 (0010)
SOUTH: int = 4  # Bit 2 (0100)
WEST: int = 8   # Bit 3 (1000)

OPPOSITE: Dict[int, int] = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
MOVE: Dict[int, Tuple[int, int]] = {
    NORTH: (-1, 0), EAST: (0, 1), SOUTH: (1, 0), WEST: (0, -1)
}

# --- ANSI COLOR CODES FOR VISUALS ---
COLOR_RESET: str = "\033[0m"
COLOR_PATH: str = "\033[92m"   # Bright Green for solution
COLOR_WALL: str = "\033[90m"   # Dark Grey for boundaries
COLOR_NUM42: str = "\033[91m"  # Bright Red for the '42' bricks
COLOR_SE: str = "\033[93m"     # Bright Yellow for Start/End

THEMES: Dict[str, Dict[str, str]] = {
    "ascii": {
        "corner": "+", "h_wall": "---", "v_wall": "|",
        "h_open": "   ", "v_open": " ", "path": " • ", "block42": "███"
    },
    "blocks": {
        "corner": "█", "h_wall": "███", "v_wall": "█",
        "h_open": "   ", "v_open": " ", "path": " ░ ", "block42": "▓▓▓"
    },
    "smooth": {
        "corner": "┼", "h_wall": "───", "v_wall": "│",
        "h_open": "   ", "v_open": " ", "path": " ● ", "block42": "█▉█"
    }
}


def parse_config(config_path: str) -> Dict[str, Any]:
    """Parses a 42 configuration file ignoring comments and safe lines.

    Args:
        config_path: System string path pointing to the file.

    Returns:
        A dictionary mapping execution configuration keys.
    """
    config: Dict[str, Any] = {
        "WIDTH": 20, "HEIGHT": 15, "ENTRY": (0, 0), "EXIT": (19, 14),
        "OUTPUT_FILE": "maze.txt", "PERFECT": True, "SEED": None,
        "ALGORITHM": "dfs", "DISPLAY_MODE": "ascii"
    }
    
    if not os.path.isfile(config_path):
        print(f"⚠️ Warning: '{config_path}' not found. Using default configs.")
        return config

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key, value = key.strip(), value.strip()
                try:
                    if "," in value and not value.startswith("("):
                        value = f"({value})"
                    config[key] = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    config[key] = value
    except Exception as error:
        print(f"❌ Critical Error reading config: {error}")
        sys.exit(1)
        
    return config


class MazeGenerator:
    """The mandatory standalone reusable maze generator engine class."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initializes dependencies and dimensions from safe config mappings."""
        self.width: int = int(config["WIDTH"])
        self.height: int = int(config["HEIGHT"])
        
        c_entry: Tuple[int, int] = config["ENTRY"]
        c_exit: Tuple[int, int] = config["EXIT"]
        self.entry: Tuple[int, int] = (c_entry[1], c_entry[0])
        self.exit: Tuple[int, int] = (c_exit[1], c_exit[0])
        
        self.output_file: str = str(config["OUTPUT_FILE"])
        self.perfect: bool = bool(config["PERFECT"])
        self.display_mode: str = str(config.get("DISPLAY_MODE", "ascii"))
        
        seed_val: Optional[int] = config.get("SEED")
        self.seed: int = seed_val if seed_val is not None else random.randint(0, 100000)
        random.seed(self.seed)
        
        self.grid: List[List[int]] = [[15 for _ in range(self.width)] for _ in range(self.height)]
        self.path_solution: List[str] = []
        
        self.p_rows: int = 5
        self.p_cols: int = 9
        self.pattern: List[List[int]] = [
            [1, 0, 1, 0, 1, 1, 1, 1, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 1, 1, 1, 1],
            [0, 0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0, 1, 1, 1, 1]
        ]

    def generate(self) -> None:
        """Carves paths matching all Section IV.4 constraints and cell coherence."""
        has_42: bool = self.height >= self.p_rows + 2 and self.width >= self.p_cols + 2
        closed_cells: Set[Tuple[int, int]] = set()

        # --- FIX: Safe boundaries isolation for small mazes ---
        if has_42:
            start_r: int = (self.height - self.p_rows) // 2
            start_c: int = (self.width - self.p_cols) // 2
            for r in range(self.p_rows):
                for c in range(self.p_cols):
                    if self.pattern[r][c] == 1:
                        grid_r, grid_c = start_r + r, start_c + c
                        self.grid[grid_r][grid_c] = 15
                        closed_cells.add((grid_r, grid_c))
                        
                        for direction, (dr, dc) in MOVE.items():
                            nr, nc = grid_r + dr, grid_c + dc
                            if 0 <= nr < self.height and 0 <= nc < self.width:
                                self.grid[nr][nc] |= OPPOSITE[direction]
        else:
            print("⚠️ Error: Maze size too small to inject the visible '42' pattern safely.")

        visited: List[List[bool]] = [[False for _ in range(self.width)] for _ in range(self.height)]
        for r, c in closed_cells:
            visited[r][c] = True

        stack: List[Tuple[int, int]] = [self.entry]
        visited[self.entry[0]][self.entry[1]] = True

        while stack:
            curr_r, curr_c = stack[-1]
            neighbors: List[Tuple[int, int, int]] = []
            for direction, (dr, dc) in MOVE.items():
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    if not visited[nr][nc]:
                        neighbors.append((direction, nr, nc))

            if neighbors:
                direction, nr, nc = random.choice(neighbors)
                if self.would_create_3x3_open_space(curr_r, curr_c, direction):
                    visited[nr][nc] = True
                    continue

                self.grid[curr_r][curr_c] &= ~direction
                self.grid[nr][nc] &= ~OPPOSITE[direction]
                visited[nr][nc] = True
                stack.append((nr, nc))
            else:
                stack.pop()

        for c in range(self.width):
            self.grid[0][c] |= NORTH
            self.grid[self.height - 1][c] |= SOUTH
        for r in range(self.height):
            self.grid[r][0] |= WEST
            self.grid[r][self.width - 1] |= EAST

    def would_create_3x3_open_space(self, r: int, c: int, direction: int) -> bool:
        """Validates corridor widths constraint to avoid large open areas."""
        dr, dc = MOVE[direction]
        nr, nc = r + dr, c + dc
        orig_curr, orig_neigh = self.grid[r][c], self.grid[nr][nc]
        
        self.grid[r][c] &= ~direction
        self.grid[nr][nc] &= ~OPPOSITE[direction]
        
        open_count: int = 0
        for i in range(max(0, r - 1), min(self.height, r + 2)):
            for j in range(max(0, c - 1), min(self.width, c + 2)):
                if self.grid[i][j] == 0:
                    open_count += 1
                    
        self.grid[r][c], self.grid[nr][nc] = orig_curr, orig_neigh
        return open_count >= 4

    def solve(self) -> bool:
        """Finds shortest route using strict BFS metrics."""
        queue: List[List[Tuple[int, int]]] = [[self.entry]]
        visited: Set[Tuple[int, int]] = {self.entry}
        dir_letters: Dict[int, str] = {NORTH: "N", EAST: "E", SOUTH: "S", WEST: "W"}

        while queue:
            path: List[Tuple[int, int]] = queue.pop(0)
            curr_r, curr_c = path[-1]

            if (curr_r, curr_c) == self.exit:
                letters: List[str] = []
                for i in range(len(path) - 1):
                    r1, c1 = path[i]
                    r2, c2 = path[i + 1]
                    for d, (dr, dc) in MOVE.items():
                        if r1 + dr == r2 and c1 + dc == c2:
                            letters.append(dir_letters[d])
                self.path_solution = letters
                return True

            curr_walls: int = self.grid[curr_r][curr_c]
            for direction, (dr, dc) in MOVE.items():
                if not (curr_walls & direction):
                    nr, nc = curr_r + dr, curr_c + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        if (nr, nc) not in visited:
                            visited.add((nr, nc))
                            queue.append(path + [(nr, nc)])
        return False

    def display(self, show_solution: bool = False) -> None:
        """Renders the maze applying terminal colors and chosen style themes."""
        style: Dict[str, str] = THEMES.get(self.display_mode, THEMES["ascii"])
        sol_coords: Set[Tuple[int, int]] = set()
        
        if show_solution and self.path_solution:
            curr_r, curr_c = self.entry
            sol_coords.add((curr_r, curr_c))
            dir_map: Dict[str, int] = {"N": NORTH, "E": EAST, "S": SOUTH, "W": WEST}
            for move in self.path_solution:
                dr, dc = MOVE[dir_map[move]]
                curr_r, curr_c = curr_r + dr, curr_c + dc
                sol_coords.add((curr_r, curr_c))

        print(COLOR_WALL + style["corner"] + (style["h_wall"] + style["corner"]) * self.width + COLOR_RESET)
        for r in range(self.height):
            row_str: str = COLOR_WALL + style["v_wall"] + COLOR_RESET
            for c in range(self.width):
                if (r, c) == self.entry:
                    cell_char: str = f"{COLOR_SE} S {COLOR_RESET}"
                elif (r, c) == self.exit:
                    cell_char = f"{COLOR_SE} E {COLOR_RESET}"
                elif (r, c) in sol_coords:
                    cell_char = f"{COLOR_PATH}{style['path']}{COLOR_RESET}"
                elif self.grid[r][c] == 15:
                    cell_char = f"{COLOR_NUM42}{style['block42']}{COLOR_RESET}"
                else:
                    cell_char = "   "

                wall_east: str = f"{COLOR_WALL}{style['v_wall']}{COLOR_RESET}" if (self.grid[r][c] & EAST) else style["v_open"]
                row_str += cell_char + wall_east
            print(row_str)

            bottom_str: str = COLOR_WALL + style["corner"] + COLOR_RESET
            for c in range(self.width):
                wall_south: str = f"{COLOR_WALL}{style['h_wall']}{COLOR_RESET}" if (self.grid[r][c] & SOUTH) else style["h_open"]
                bottom_str += wall_south + f"{COLOR_WALL}{style['corner']}{COLOR_RESET}"
            print(bottom_str)

    def save_to_file(self) -> None:
        """Saves matrix exactly matching Section IV.5 rules with trailing \\n."""
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                for r in range(self.height):
                    hex_row: str = "".join([hex(self.grid[r][c])[2:].upper() for c in range(self.width)])
                    f.write(hex_row + "\n")
                f.write("\n")
                f.write(f"{self.entry[1]},{self.entry[0]}\n")
                f.write(f"{self.exit[1]},{self.exit[0]}\n")
                f.write("".join(self.path_solution) + "\n")
        except IOError as err:
            print(f"❌ Error writing to output file: {err}")


def interactive_menu(config_file: str) -> None:
    """Controls interactive loop execution menu handles."""
    config: Dict[str, Any] = parse_config(config_file)
    current_maze: Optional[MazeGenerator] = None

    while True:
        current_mode: str = config.get("DISPLAY_MODE", "ascii").upper()
        print("\n" + "=" * 45)
        print(f"     A-MAZE-ING MENU [CURRENT STYLE: {current_mode}]")
        print("=" * 45)
        print("1. Generate New Random Maze")
        print("2. Display Generated Maze")
        print("3. Solve & Show Visual Path (Colored)")
        print("4. Save Generated Output to File")
        print("5. Configure Live Dimensions")
        print("6. Change Visual Style Format (ASCII / Unicode)")
        print("7. Exit Program")
        print("=" * 45)

        choice: str = input("Select an option (1-7): ").strip()

        if choice == "1":
            config["SEED"] = random.randint(1, 999999)
            current_maze = MazeGenerator(config)
            current_maze.generate()
            print(f"✔️ Maze successfully initialized with Seed: {config['SEED']}!")
            current_maze.display(show_solution=False)
        elif choice == "2":
            if current_maze:
                current_maze.display(show_solution=False)
            else:
                print("❌ Generate a maze first (Option 1)!")
        elif choice == "3":
            if current_maze:
                if current_maze.solve():
                    current_maze.display(show_solution=True)
                    print(f"Path Instructions: {''.join(current_maze.path_solution)}")
                else:
                    print("❌ No valid path could be found from Start to End.")
            else:
                print("❌ Generate a maze first (Option 1)!")
        elif choice == "4":
            if current_maze:
                if not current_maze.path_solution:
                    current_maze.solve()
                current_maze.save_to_file()
                print(f"✔️ Hex data exported successfully to '{current_maze.output_file}'!")
            else:
                print("❌ Generate a maze first (Option 1)!")
        elif choice == "5":
            try:
                w = int(input("Enter Width: "))
                h = int(input("Enter Height: "))
                if w <= 1 or h <= 1:
                    print("❌ Error: Dimensions must be greater than 1x1.")
                    continue
                config["WIDTH"] = w
                config["HEIGHT"] = h
                # Adjust exit according to new scale
                config["EXIT"] = (w - 1, h - 1)
                print("✔️ Settings temporarily updated!")
            except ValueError:
                print("❌ Invalid integers.")
        elif choice == "6":
            print("\n1. ASCII (Default) | 2. Blocks | 3. Smooth Lines")
            sub_choice: str = input("Choose style: ").strip()
            if sub_choice == "1":
                config["DISPLAY_MODE"] = "ascii"
            elif sub_choice == "2":
                config["DISPLAY_MODE"] = "blocks"
            elif sub_choice == "3":
                config["DISPLAY_MODE"] = "smooth"
            if current_maze:
                current_maze.display_mode = config["DISPLAY_MODE"]
        elif choice == "7":
            sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Error: Missing configuration file argument!!!")
        print("Usage: python3 a_maze_ing.py <config_file_path>")
        sys.exit(1)
    interactive_menu(sys.argv[1])
