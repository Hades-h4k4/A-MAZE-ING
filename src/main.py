"""Main interactive menu entry point."""

import random
import sys
from typing import Dict, Any, Optional
from src.config_parser import parse_config
from src.generator import MazeGenerator

COLOR_RESET: str = "\033[0m"
COLOR_PATH: str = "\033[92m"
COLOR_WALL: str = "\033[90m"
COLOR_NUM42: str = "\033[91m"
COLOR_SE: str = "\033[93m"

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
        print("6. Change Visual Style Format")
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
                print("❌ Generate a maze first!")
        elif choice == "3":
            if current_maze:
                if current_maze.solve():
                    current_maze.display(show_solution=True)
                    print(f"Path Instructions: {''.join(current_maze.path_solution)}")
                else:
                    print("❌ No valid path found.")
            else:
                print("❌ Generate a maze first!")
        elif choice == "4":
            if current_maze:
                if not current_maze.path_solution:
                    current_maze.solve()
                current_maze.save_to_file()
                print(f"✔️ Hex data exported successfully to '{current_maze.output_file}'!")
            else:
                print("❌ Generate a maze first!")
        elif choice == "5":
            try:
                w = int(input("Enter Width: "))
                h = int(input("Enter Height: "))
                if w <= 1 or h <= 1:
                    print("❌ Error: Dimensions must be greater than 1x1.")
                    continue
                config["WIDTH"] = w
                config["HEIGHT"] = h
                config["EXIT"] = (w - 1, h - 1)
                print("✔️ Settings temporarily updated!")
            except ValueError:
                print("❌ Invalid integers.")
        elif choice == "6":
            print("\n1. ASCII | 2. Blocks | 3. Smooth Lines")
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
        print("Usage: python3 -m src.main <config_file_path>")
        sys.exit(1)
    interactive_menu(sys.argv[1])
