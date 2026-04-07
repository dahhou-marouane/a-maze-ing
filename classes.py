import os
from dataclasses import dataclass
from typing import List, Tuple, Dict
from mazegen import MazeGenerator


@dataclass
class Config:
    """Immutable maze settings parsed from the config file."""

    width: int
    height: int
    entry: Tuple[int, int]
    exit_pos: Tuple[int, int]
    perfect: bool
    seed: str | None
    output_file: str


class DisplayConfig:
    """Manages visual settings: colors, characters, and display state."""

    _colorado: List[str] = [
        "\033[0m",
        "\033[31m",
        "\033[91m",
        "\033[92m",
        "\033[93m",
        "\033[94m",
        "\033[95m",
        "\033[96m",
    ]
    _emoji: List[str] = ["██", "42", "$$", "@@", "##", "**", "&&", "MM", "00"]
    _emoji2: List[str] = ["▓▓", "13", "%%", "++", "NN"]
    wall_char: str = _emoji[0]
    path_char: str = _emoji2[0]
    wall_color: str = ""
    path_color: str = ""
    _w: int = -1
    _wc: int = -1
    _p: int = -1
    _pc: int = -1
    path: bool = False
    old_col: int = 0
    old_rows: int = 0

    def new_wall_color(self) -> None:
        """Cycles to the next wall color."""

        self._w += 1
        self.wall_color = self._colorado[(self._w + 1) % len(self._colorado)]

    def new_wall_char(self) -> None:
        """Cycles to the next wall character."""

        self._wc += 1
        self.wall_char = self._emoji[(self._wc + 1) % len(self._emoji)]

    def new_path_color(self) -> None:
        """Cycles to the next path color."""

        self._p += 1
        self.path_color = self._colorado[(self._p + 1) % len(self._colorado)]

    def new_path_char(self) -> None:
        """Cycles to the next path character."""

        self._pc += 1
        self.path_char = self._emoji2[(self._pc + 1) % len(self._emoji2)]


class MazeState:
    """Holds the generated maze data and owns the generation lifecycle."""

    def __init__(self, config: Config) -> None:
        """Initialises an empty maze state from the given config.

        Args:
            config: Validated maze settings to generate from.
        """

        self.config = config
        self.grid: List[List[str]] = []
        self.maze: List[List[Dict[str, bool]]] = []
        self.solution: str = ""

    def regenerate(self) -> None:
        """Re-generates the maze and updates grid, maze, and solution."""

        gen = MazeGenerator(
            width=self.config.width,
            height=self.config.height,
            entry=self.config.entry,
            exit=self.config.exit_pos,
            perfect=self.config.perfect,
            seed=self.config.seed,
        )
        try:
            gen.generate()
        except ValueError as e:
            os.system("clear")
            print("ERROR:", e)
            exit(1)
        self.maze = gen.maze()
        self.solution = gen.solution()
        write_output(self, self.config)


def write_output(state: MazeState, config: Config) -> None:
    """Writes the maze grid and solution to the output file.

    Args:
        state: Current maze state containing the grid and solution.
        config: Config holding the output file path.
    """

    wall_direction: Dict[str, int] = {"N": 1, "E": 2, "S": 4, "W": 8}
    try:
        with open(config.output_file, "w") as f:
            for row in range(config.height):
                for col in range(config.width):
                    sum: int = 0
                    for direction, wall in wall_direction.items():
                        if state.maze[row][col][direction]:
                            sum += wall
                    f.write(hex(sum)[2:].upper())
                f.write("\n")
            f.write("\n")
            f.write(f"{config.entry[0]},{config.entry[1]}\n")
            f.write(f"{config.exit_pos[0]},{config.exit_pos[1]}\n")
            f.write(f"{state.solution}\n")
    except (PermissionError, IsADirectoryError) as e:
        os.system("clear")
        print(f"ERROR output_file: {e.__class__.__name__}")
        exit(1)
