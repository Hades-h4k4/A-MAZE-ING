"""Configuration file parsing sub-module."""

import ast
import os
import sys
from typing import Dict, Any


def parse_config(config_path: str) -> Dict[str, Any]:
    """Parses a 42 configuration file ignoring comments."""
    config: Dict[str, Any] = {
        "WIDTH": 20, "HEIGHT": 15, "ENTRY": (0, 0), "EXIT": (19, 14),
        "OUTPUT_FILE": "maze.txt", "PERFECT": True, "SEED": None,
        "ALGORITHM": "dfs", "DISPLAY_MODE": "ascii"
    }

    if not os.path.isfile(config_path):
        print(f"⚠️ Warning: '{config_path}' not found. Using defaults.")
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
