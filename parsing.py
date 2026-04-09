from typing import List, Dict, Tuple
import sys
import os
from classes import Config


def parse_config() -> Config:
    """read the config file and validate it and parse it to dict"""
    config_file = sys.argv[1]

    def _check_output_file(file: str) -> None:
        if not file:
            print("Error config file: OUTPUT_FILE cannot be ''")
            sys.exit(1)
        allowed_dir = os.path.dirname(os.path.realpath(__file__))
        output_path = os.path.realpath(os.path.join(allowed_dir, file))
        if os.path.dirname(output_path) != allowed_dir:
            os.system("clear")
            print(
                "Error config file: OUTPUT_FILE"
                " must be in the script directory")
            sys.exit(1)

    config: Dict[str, str] = {}
    keys: List[str] = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT"
    ]
    try:
        with open(config_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(f"Bad config line [{line}]")
                key, value = line.split("=", 1)
                config[key.upper().strip()] = value.strip()
    except (
        FileNotFoundError,
        IsADirectoryError,
        PermissionError,
        ValueError
    ) as e:
        print("Error:", e)
        sys.exit(1)
    for key, _ in config.items():
        if key not in keys:
            if key == "SEED":
                continue
            print(f"Error config file: Unknown key [{key}] in config file")
            sys.exit(1)
    for ky in keys:
        if ky not in config:
            print(f"Error: missing key [{ky}] in config file")
            sys.exit(1)
    try:
        try:
            width: int = int(config["WIDTH"])
        except ValueError:
            raise ValueError("Invalid int value of width")

        try:
            height: int = int(config["HEIGHT"])
        except ValueError:
            raise ValueError("Invalid int value of height")

        try:
            entry_x, entry_y = config["ENTRY"].strip("() ").split(",")
            entry_pos: Tuple[int, int] = (int(entry_x), int(entry_y))
        except ValueError:
            raise ValueError(
                f"Invalid ENTRY position: '{config['ENTRY']}' "
                f"(expected format: (x,y))"
            )

        try:
            exit_x, exit_y = config["EXIT"].strip("() ").split(",")
            exit_pos: Tuple[int, int] = (int(exit_x), int(exit_y))
        except ValueError:
            raise ValueError(
                f"Invalid EXIT position: '{config['EXIT']}' "
                f"(expected format: (x,y))"
            )

        if "SEED" not in config:
            seed: str | None = None
        elif config["SEED"].strip() == "":
            raise ValueError("SEED must have a value")
        else:
            seed = config["SEED"]
        perfect_str: str = config["PERFECT"].strip().lower()
        perfect: bool
        if perfect_str in ("true", "1"):
            perfect = True
        elif perfect_str in ("false", "0"):
            perfect = False
        else:
            raise ValueError("Invalid boolean value of perfect maze")
    except ValueError as e:
        print(f"Error config file: {e}")
        sys.exit(1)
    if width <= 0 or height <= 0:
        print("WIDTH and HEIGHT must be positive integers > 0")
        sys.exit(1)
    if not (0 <= entry_pos[0] < width and 0 <= entry_pos[1] < height):
        print("Error: ENTRY is outside the maze walls")
        sys.exit(1)
    if not (0 <= exit_pos[0] < width and 0 <= exit_pos[1] < height):
        print("Error: EXIT is outside the maze walls")
        sys.exit(1)
    if entry_pos == exit_pos:
        print("Error: ENTRY and EXIT must be different")
        sys.exit(1)
    _check_output_file(config["OUTPUT_FILE"])
    return Config(
        width=width,
        height=height,
        entry=entry_pos,
        exit_pos=exit_pos,
        output_file=config["OUTPUT_FILE"],
        perfect=perfect,
        seed=seed,
    )
