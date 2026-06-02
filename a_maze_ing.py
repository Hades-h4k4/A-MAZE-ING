import os
import sys


root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.main import interactive_menu  # noqa: E402


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Error: Missing configuration file argument!!!")
        print("Usage: python3 a_maze_ing.py <config_file_path>")
        sys.exit(1)

    interactive_menu(sys.argv[1])
