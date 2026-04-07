import select
import tty
import termios
import os
import time
import sys
from typing import List, Dict, Tuple
from mazegen import MazeGenerator
from dataclasses import dataclass


@dataclass
class Config:
    """Immutable settings parsed from the config file."""
    width: int
    height: int
    entry: Tuple[int, int]
    exit_pos: Tuple[int, int]
    prefect: bool
    seed: str | None
    output_file: str


class DisplayConfig:
    _colorado: List[str] = ['\033[0m', '\033[31m', '\033[91m',
                           '\033[92m', '\033[93m', '\033[94m',
                           '\033[95m', '\033[96m']
    _emoji: List[str] = ['██', '42', '$$', '@@', '##', '🌲', '🍄', '🔥']
    _emoji2: List[str] = ['▓▓', '🐭', '🐾', '🌟',
                         '🍬', '💎', '🔮', '🍪', '👣', '42', '@@']
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

    def new_wall_colol(self) -> None:
        self._w += 1
        self.wall_color = self._colorado[(self._w + 1) % len(self._colorado)]

    def new_wall_char(self) -> None:
        self._wc += 1
        self.wall_char = self._emoji[(self._wc + 1) % len(self._emoji)]

    def new_path_colol(self) -> None:
        self._p += 1
        self.path_color = self._colorado[(self._p + 1) % len(self._colorado)]

    def new_path_char(self) -> None:
        self._pc += 1
        self.path_char = self._emoji2[(self._pc + 1 )% len(self._emoji2)]


class MazeState:
    
    def __init__(self, config: Config) -> None:
        self.config = config
        self.grid: List[List[str]] = []
        self.maze: List[List[Dict[str, bool]]] = []
        self.solution: str = ""

    def regenerate(self) -> None:
        gen = MazeGenerator(
                width=self.config.width,
                height=self.config.height,
                entry=self.config.entry,
                exit=self.config.exit_pos,
                prefect=self.config.prefect,
                seed=self.config.seed
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
    wall_direction: Dict[str, int] = {'N': 1, 'E': 2, 'S': 4, 'W': 8}
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
    except (FileNotFoundError, PermissionError, IsADirectoryError):
        print("s")

def parse_config() -> Config:
    """read the config file and validate it and parse it to dict"""
    config_file = sys.argv[1]
    def _check_output_file(file: str) -> None:
        if not file:
            print("Error config file: OUTPUT_FILE cannot be ''")
            exit(1)
        allowed_dir = os.path.dirname(os.path.realpath(__file__))
        output_path = os.path.realpath(os.path.join(allowed_dir, file))
        if os.path.dirname(output_path) != allowed_dir:
            os.system("clear")
            print("Error config file: OUTPUT_FILE must be in the "
                  "script directory")
            exit(1)

    config: Dict[str, str] = {}
    keys: List[str] = ["WIDTH", "HEIGHT",
                       "ENTRY", "EXIT", "OUTPUT_FILE", "PREFECT"]
    try:
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    raise ValueError(f"Bad config line [{line}]")
                key, value = line.split('=', 1)
                config[key.upper().strip()] = value.strip()
    except (FileNotFoundError, IsADirectoryError,
            PermissionError, ValueError) as e:
        print("Error:", e)
        exit(1)
    for ky in keys:
        if ky not in config:
            print(f"Error: missing key [{ky}] in config file")
            exit(1)
    try:
        try:
            width: int = int(config['WIDTH'])
        except ValueError as e:
            raise ValueError("Invalid int value of width")

        try:
            height: int = int(config['HEIGHT'])
        except ValueError:
            raise ValueError("Invalid int value of height")

        try:
            entry_x, entry_y = config['ENTRY'].strip("() ").split(',')
            entry_pos: Tuple[int, int] = (int(entry_x), int(entry_y))
        except ValueError:
            raise ValueError(f"Invalid ENTRY position: '{config['ENTRY']}' (expected format: (x,y))")

        try:
            exit_x, exit_y = config['EXIT'].strip("() ").split(',')
            exit_pos: Tuple[int, int] = (int(exit_x), int(exit_y))
        except ValueError:
            raise ValueError(f"Invalid EXIT position: '{config['EXIT']}' (expected format: (x,y))")

        if "SEED" not in config:
            seed: str | None = None
        elif config['SEED'].strip() == "":
            raise ValueError("SEED must have a value")
        else:
            seed = config['SEED']
        prefect: str | bool = config['PREFECT'].strip().lower()
        if prefect in ("true", "1"):
            prefect = True
        elif prefect in ("false", "0"):
            prefect = False
        else:
            raise ValueError("Invalid boolean value of prefect maze")
    except ValueError as e:
        print(f"Error config file: {e}")
        exit(1)
    if width <= 0 or height <= 0:
        print("WIDTH and HEIGHT must be positive integers > 0")
        exit(1)
    if not (0 <= entry_pos[0] < width and 0 <= entry_pos[1] < height):
        print("Error: ENTRY is outside the maze walls")
        exit(1)
    if not (0 <= exit_pos[0] < width and 0 <= exit_pos[1] < height):
        print("Error: EXIT is outside the maze walls")
        exit(1)
    if entry_pos == exit_pos:
        print("Error: ENTRY and EXIT must be different")
        exit(1)
    _check_output_file(config['OUTPUT_FILE'])
    return Config(
        width= width,
        height=height,
        entry= entry_pos,
        exit_pos= exit_pos,
        output_file= config['OUTPUT_FILE'],
        prefect= prefect,
        seed=seed
        )


def grid_print(state: MazeState, config: Config) -> None:
    cols, rows = os.get_terminal_size()
    if cols < (config.width * 2 + 1) * 2 + 1  or rows < config.height * 2 + 12:
        os.system("clear")
        middel_print("Terminal is small to print the maze")
        return
    spaces: int = (cols - (config.width * 2 + 1) * 2) // 2
    new_lines: int = (rows - (config.height * 2 + 1)) // 2
    os.system("clear")
    print("\n" * new_lines)
    for _ in state.grid:
        print(" " * spaces, end="")
        for i in _:
            print(i, end="")
        print()
    if config.height < 9 or config.width < 9:
        middel_print("The maze is small to add the 42_stamp")


def print_maze(state: MazeState, config: Config, display: DisplayConfig) -> None:
    stamp: List[Tuple[int, int]] = [
                # 4
                (0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (3, 2), (4, 2),
                # 2
                (0, 4), (0, 5), (0, 6), (1, 6), (2, 4), (2, 5), (2, 6), (3, 4), (4, 4),
                (4, 5), (4, 6)
                ]
    start_row = (config.height - 5) // 2
    start_col = (config.width  - 7) // 2
    rows: int = config.height * 2 + 1
    cols: int = config.width * 2 + 1
    state.grid = [[display.wall_color + display.wall_char + '\033[0m'] * (cols) for _ in range(rows)]
    for row in range(config.height):
        for col in range(config.width):
            cell = state.maze[row][col]
            cr: int = row * 2 + 1
            cc: int = col * 2 + 1
            state.grid[cr][cc] = '  '
            if cr == config.entry[1] * 2 + 1 and cc == config.entry[0] * 2 + 1:
                state.grid[cr][cc] = '\033[102m' + 'EN' + '\033[0m'
            elif cr == config.exit_pos[1] * 2 + 1 and cc == config.exit_pos[0] * 2 + 1:
                state.grid[cr][cc] = '\033[101m' + 'EX' + '\033[0m'
            if not cell['N']:
                state.grid[cr - 1][cc] = '  '
            if not cell['S']:
                state.grid[cr + 1][cc] = '  '
            if not cell['E']:
                state.grid[cr][cc + 1] = '  '
            if not cell['W']:
                state.grid[cr][cc - 1] = '  '
    if config.height > 8 or config.width > 8:
        for r, c in stamp:
            state.grid[(r + start_row) * 2 + 1][(c + start_col) * 2 + 1] = display.wall_color + display.wall_char + '\033[0m'
    grid_print(state=state, config=config)
    maze_controle()

def print_path(state: MazeState, config: Config, display: DisplayConfig) -> None:
    if state.solution:
        cr: int = config.entry[1] * 2 + 1
        cc: int = config.entry[0] * 2 + 1
        for move in state.solution:
            state.grid[cr][cc] = display.path_color + display.path_char + '\033[0m'
            if cr == config.entry[1] * 2 + 1 and cc == config.entry[0] * 2 + 1:
                state.grid[cr][cc] = '\033[102m' + 'EN' + '\033[0m'
            if move == 'N':
                state.grid[cr - 1][cc] = display.path_color + display.path_char + '\033[0m'
                cr -= 2
            elif move == 'S':
                state.grid[cr + 1][cc] = display.path_color + display.path_char + '\033[0m'
                cr += 2
            elif move == 'E':
                state.grid[cr][cc + 1] = display.path_color + display.path_char + '\033[0m'
                cc += 2
            elif move == 'W':
                state.grid[cr][cc - 1] = display.path_color + display.path_char + '\033[0m'
                cc -= 2
            else:
                print("Error: Invalid path")
                exit(1)
    grid_print(state=state, config=config)
    maze_controle()


def welcom() -> None:
    welcom_msg: List[str] = [
        " " * 24 + "██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗██" +
        "█████╗",
        " " * 24 + "██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██" +
        "╔════╝",
        " " * 24 + "██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║██" +
        "███╗",
        " " * 24 + "██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██" +
        "╔══╝",
        " " * 24 + "╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║██" +
        "█████╗",
        " " * 24 + " ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═" +
        "═════╝",
        "\n",
        " " * 48 + "████████╗ ██████╗",
        " " * 48 + "╚══██╔══╝██╔═══██╗",
        " " * 48 + "   ██║   ██║   ██║",
        " " * 48 + "   ██║   ██║   ██║",
        " " * 48 + "   ██║   ╚██████╔╝",
        " " * 48 + "   ╚═╝    ╚═════╝",
        "\n",
        "███╗   ███╗ █████╗ ███████╗███████╗     ██████╗ ███████╗███╗   ██╗" +
        "███████╗██████╗  █████╗ ████████╗ ██████╗ ██████╗",
        "████╗ ████║██╔══██╗╚══███╔╝██╔════╝    ██╔════╝ ██╔════╝████╗  ██║" +
        "██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗",
        "██╔████╔██║███████║  ███╔╝ █████╗      ██║  ███╗█████╗  ██╔██╗ ██║" +
        "█████╗  ██████╔╝███████║   ██║   ██║   ██║██████╔╝",
        "██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝      ██║   ██║██╔══╝  ██║╚██╗██║" +
        "██╔══╝  ██╔══██╗██╔══██║   ██║   ██║   ██║██╔══██╗",
        "██║ ╚═╝ ██║██║  ██║███████╗███████╗    ╚██████╔╝███████╗██║ ╚████║" +
        "███████╗██║  ██║██║  ██║   ██║   ╚██████╔╝██║  ██║",
        "╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝" +
        "╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝",
        " " * 106 + "\033[4m" "by mdahhou"
    ]
    cols, rows = os.get_terminal_size()
    spaces: int = (cols - 116) // 2
    new_lines: int = (rows - 20) // 2
    if cols < 117 or rows < 24:
        os.system("clear")
        middel_print("Terminal is too small make it bigger")
        while True:
            cols, rows = os.get_terminal_size()
            if cols >= 117 and rows >= 24:
                break
    os.system("clear")
    print("\n" * new_lines)
    for msg in welcom_msg:
        print('\033[31m' + '\033[5m' + " " * spaces + msg + '\033[0m')
    print('\033[92m' + '\033[5m' + ((" " * 46) + " " * spaces) +
          "Press 'S' to START!!" + '\033[0m')


def exit_code() -> None:
    def _good_bye() -> None:
        good_msg: List[str] = [
            " ██████╗  ██████╗  ██████╗ ██████╗",
            "██╔════╝ ██╔═══██╗██╔═══██╗██╔══██╗",
            "██║  ███╗██║   ██║██║   ██║██║  ██║",
            "██║   ██║██║   ██║██║   ██║██║  ██║",
            "╚██████╔╝╚██████╔╝╚██████╔╝██████╔╝",
            " ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝ ",
            " " * 5 + "██████╗ ██╗   ██╗███████╗",
            " " * 5 + "██╔══██╗╚██╗ ██╔╝██╔════╝",
            " " * 5 + "██████╔╝ ╚████╔╝ █████╗  ",
            " " * 5 + "██╔══██╗  ╚██╔╝  ██╔══╝  ",
            " " * 5 + "██████╔╝   ██║   ███████╗",
            " " * 5 + "╚═════╝    ╚═╝   ╚══════╝",
            " " * 25 + "\033[4m" "by mdahhou"
        ]
        try:
            os.system("clear")
            cols, rows = os.get_terminal_size()
            spaces: int = (cols - 34) // 2
            print("\n" * rows)
            for msg in good_msg:
                print('\033[31m' + " " * spaces + msg + '\033[0m')
            for _ in range(rows):
                print()
                time.sleep(0.04)
            os.system("clear")
        except KeyboardInterrupt:
            os.system("clear")
    _good_bye()
    exit(0)


def middel_print(message: str) -> None:
    cols, _ = os.get_terminal_size()
    spaces: int = (cols - len(message)) // 2
    print((" " * spaces) +
          message + '\033[0m')

def handel_exit(is_welcom: bool = False) -> None:

    middel_print("Do u want really to " +
                         '\033[31m' + "EXIT" + '\033[0m' +
                         ": (Y)es, (N)o"
                         )
    while True:
        char = get_char()
        if char in ['Y', 'y']:
            exit_code()
        elif char in ['N', 'n']:
            if is_welcom:
                welcom()
                break

def redraw(state: MazeState, config: Config, display: DisplayConfig) -> None:
    if display.path:
        print_path(state=state, config=config, display=display)
    else:
        print_maze(state=state, config=config, display=display)


def maze_controle() -> None:
    print("\n" * 3)
    msg: List[str] = ["PRESS: " +
                      '\033[31m' + "(Q,q) to QUIT" + '\033[0m' +
                      " ; (R,r) to REGENERATE ; (P,p) to Show PATH;",
                      "(1) to change walls COLORS    ;",
                      "(2) to change path COLORS     ;",
                      "(3) to change walls CHARACTERS;",
                      "(4) to change path CHARACTERS  "
                      ]
    for i in msg:
        middel_print(i)


def main() -> None:
    config: Config
    state: MazeState
    display = DisplayConfig()
    old_col: int = 0
    old_rows: int = 0
    def _check_terminal(is_welcom: bool = False) -> None:
        nonlocal old_col, old_rows
        new_col, new_rows = os.get_terminal_size()
        if (old_col, old_rows) != (new_col, new_rows):
            if is_welcom:
                welcom()
            else:
                nonlocal state, config, display
                redraw(state=state, config=config, display=display)
        old_col = new_col
        old_rows = new_rows

    if len(sys.argv) == 1:
        print("Error: The program must be run with the following command:\n"
              "python3 a_maze_ing.py [config_file_here]")
        exit(1)
    while True:
        char: str = get_char()
        _check_terminal(True)
        if char in ['S', 's']:
            os.system("clear")
            config = parse_config()
            state = MazeState(config=config)
            state.regenerate()
            write_output(state=state, config=config)
            print_maze(state=state, config=config, display=display)
            while True:
                char = get_char()
                _check_terminal()
                if char in ['R', 'r']:
                    config = parse_config()
                    state = MazeState(config=config)
                    state.regenerate()
                    print_maze(state=state, config=config, display=display)
                    display.path = False
                elif char in ['P', 'p']:
                    if not display.path:
                        print_path(state=state, config=config, display=display)
                        display.path = True
                    else:
                        print_maze(state=state, config=config, display=display)
                        display.path = False
                elif char == '1':
                    display.new_wall_colol()
                    print_maze(state=state, config=config, display=display)
                    if display.path:
                        print_path(state=state, config=config, display=display)
                elif char == '2':
                    display.new_path_colol()
                    if display.path:
                        print_path(state=state, config=config, display=display)
                elif char == '3':
                    display.new_wall_char()
                    print_maze(state=state, config=config, display=display)
                    if display.path:
                        print_path(state=state, config=config, display=display)
                elif char == '4':
                    display.new_path_char()
                    if display.path:
                        print_path(state=state, config=config, display=display)
                elif char in ['Q', 'q']:
                    middel_print("Do u want really to " +
                                 '\033[31m' + "EXIT" + '\033[0m' +
                                 ": (Y)es, (N)o"
                                 )
                    while True:
                        char = get_char()
                        if char in ['Y', 'y']:
                            exit_code()
                        elif char in ['N', 'n']:
                            if display.path:
                                print_path(state=state, config=config, display=display)
                            else:
                                print_maze(state=state, config=config, display=display)
                            break
        elif char in ['Q', 'q']:
            handel_exit(True)


def get_char() -> str:
    timeout = 0.01
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)

        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            return sys.stdin.read(1)
        return ""

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        os.system('clear')
        middel_print("KeyboardInterrupt")

