import tty
import termios
import os
import time
import sys
import random
from collections import deque

DIGITS: dict[str, list[str]] = {
    '4': [
        "1 0 1",
        "1 0 1",
        "1 1 1",
        "0 0 1",
        "0 0 1",
    ],
    '2': [
        "1 1 1",
        "0 0 1",
        "1 1 1",
        "1 0 0",
        "1 1 1",
    ],
}

MOVE: dict[str, tuple[int, int]] = {
    'N': (-1,  0),
    'S': (1,  0),
    'E': (0,  1),
    'W': (0, -1)
}

OPPOSITE: dict[str, str] = {
    'N': 'S',
    'S': 'N',
    'E': 'W',
    'W': 'E'
}


class MazeGenerator:

    def __init__(self, width: int, height: int, entry: tuple[int, int], exit: tuple[int, int], output_file: str, perfect: bool, seed: str | None) -> None:
        """Store the parametres of the maze and init empty maze"""
        self._width: int = width
        self._height: int = height
        self._entry: tuple[int, int] = entry
        self._exit_pos: tuple[int, int] = exit
        self._output_file: str = output_file
        self._perfect: bool = perfect
        self._seed: str | None = seed
        self._maze: list[list[dict[str, bool]]] = []
        self._solution: str = ""

    def solution(self) -> str:
        return self._solution

    def maze(self) -> list[list[dict[str, bool]]]:
        return self._maze

    def generate(self) -> None:
        """Generate the maze with DFS algo"""
        random.seed(self._seed)
        self._maze = self._create_maze()
        self._dfs_algo()
        if not self._perfect:
            self._break_more_walls()
        self._solution = self._find_path()

    def _create_maze(self) -> list[list[dict[str, bool]]]:
        """Create maze with all the walls closed"""
        maze: list[list[dict[str, bool]]] = []
        for _ in range(self._height):
            row: list[dict[str, bool]] = []
            for _ in range(self._width):
                cell = {'N': True, 'E': True, 'S': True, 'W': True}
                row.append(cell)
            maze.append(row)
        return maze

    def _open_walls(self, row: int, col: int, direction: str) -> None:
        """Open wall between cell and neighbor cell"""
        self._maze[row][col][direction] = False
        dr, dc = MOVE[direction]
        next_row = row + dr
        next_col = col + dc
        self._maze[next_row][next_col][OPPOSITE[direction]] = False

    def _dfs_algo(self) -> None:
        """Function of dfs_algo to generate the maze by DFS algo using seed and it calls 
        the function open_walls to open the walls for the cell and it neigbor"""

        visited: list[list[bool]] = [
            [False] * self._width for _ in range(self._height)]
        stack: list[tuple[int, int]] = [(0, 0)]
        visited[0][0] = True
        while stack:
            row, col = stack[-1]
            neigbors: list[tuple[int, int, str]] = []
            for direcction in ['N', 'E', 'S', 'W']:
                dr, dc = MOVE[direcction]
                next_row = row + dr
                next_col = col + dc
                if 0 <= next_row < self._height and 0 <= next_col < self._width and not visited[next_row][next_col]:
                    neigbors.append((next_row, next_col, direcction))
            if neigbors:
                next_row, next_col, direcction = random.choice(neigbors)
                stack.append((next_row, next_col))
                visited[next_row][next_col] = True
                self._open_walls(row, col, direcction)
            else:
                stack.pop()

    def _break_more_walls(self) -> None:
        """This function is called after after dfs_algo fuction if the maze should not be prefect to break extra walls"""
        wallstobreak: int = int((self._width * self._height) * 0.15)
        breaked: int = 0
        while breaked < wallstobreak:
            row: int = random.randint(0, self._height - 1)
            col: int = random.randint(0, self._width - 1)
            direction: str = random.choice(['N', 'E', 'S', 'W'])
            dr, dc = MOVE[direction]
            next_row = row + dr
            next_col = col + dc
            if not (0 <= next_row < self._height and 0 <= next_col < self._width):
                continue
            if self._maze[row][col][direction] is False:
                continue
            self._open_walls(row, col, direction)
            breaked += 1

    def _find_path(self) -> str:
        """Find shortest path from entry to exit using BFS.
        Returns:
            Path string of N/E/S/W characters e.g. 'NNEESS'
        """
        entryc: int = self._entry[0]
        entryr: int = self._entry[1]
        exitc: int = self._exit_pos[0]
        exitr: int = self._exit_pos[1]
        visited: list[list[bool]] = [
            [False] * self._width for _ in range(self._height)]
        queue: deque[tuple[int, int, str]] = deque()
        queue.append((entryr, entryc, ""))
        visited[entryr][entryc] = True
        while queue:
            row, col, path = queue.popleft()
            if row == exitr and col == exitc:
                return path
            for direction in ['N', 'E', 'S', 'W']:
                if not self._maze[row][col][direction]:
                    dr, dc = MOVE[direction]
                    next_row = row + dr
                    next_col = col + dc
                    if not visited[next_row][next_col]:
                        visited[next_row][next_col] = True
                        queue.append((next_row, next_col, path + direction))
        return ""


def parse_config(file: str) -> dict[str, int | bool | tuple[int, int] | str | None]:
    """read the config file and validate it and parse it to dict"""
    config: dict[str, int | str] = {}
    keys: list[str] = ["WIDTH", "HEIGHT",
                       "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    try:
        with open(file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    raise ValueError(f"Bad config line [{line}]")
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    except (FileNotFoundError, IsADirectoryError, PermissionError, ValueError) as e:
        print("Error:", e)
        exit(1)
    for ky in keys:
        if ky not in config:
            print(f"Error: missing key [{ky}] in config file")
            exit(1)
    try:
        width: int = int(config['WIDTH'])
        height: int = int(config['HEIGHT'])

        entry_x, entry_y = config['ENTRY'].split(',')
        exit_x, exit_y = config['EXIT'].split(',')

        entry_pos: tuple[int, int] = (int(entry_x), int(entry_y))
        exit_pos: tuple[int, int] = (int(exit_x), int(exit_y))
        if "SEED" not in config or config['SEED'].strip() == "":
            seed: str | None = None
        else:
            seed = config['SEED']
        perfect: str | bool = config['PERFECT'].strip().lower()
        if perfect in ("true", "1"):
            perfect = True
        elif perfect in ("false", "0"):
            perfect = False
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
    return {
        'width': width,
        'height': height,
        'entry': entry_pos,
        'exit': exit_pos,
        'output_file': config['OUTPUT_FILE'],
        'perfect': perfect,
        'seed': seed
    }


BOX = {
    "NS":   "\u2551",
    "EW":   "\u2550",
    "NE":   "\u255a",
    "NW":   "\u255d",
    "SE":   "\u2554",
    "SW":   "\u2557",
    "NSE":  "\u2560",
    "NSW":  "\u2563",
    "NEW":  "\u2569",
    "SEW":  "\u2566",
    "NSEW": "\u256c",
    "N":    "\u2568",
    "S":    "\u2565",
    "E":    "\u255e",
    "W":    "\u2561",
    "":     "\u00b7",
}


motion_color = "\033[5m"
YLW_color = '\033[93m'
GRN_color = '\033[92m'
RED_color = '\033[91m'
REDDARK_color = '\033[31m'
RST_color = '\033[0m'
entry_color: str = "\033[102m"
exit_color: str = "\033[101m"

end_color: str = "\033[0m"


def grid_print(grid: list[list[str]], width: int, height: int) -> None:
    cols, rows = os.get_terminal_size()
    spaces: int = (cols - (width * 2 + 1) * 2) // 2
    new_lines: int = (rows - (height * 2 + 1)) // 2
    os.system("clear")
    print("\n" * new_lines)
    for _ in grid:
        print(" " * spaces, end="")
        for i in _:
            print(i, end="")
        print()


def print_maze(maze: list[list[dict[str, bool]]], width: int, height: int, entry: tuple[int, int], exit_pos: tuple[int, int], walls_color: str, wall_char: str = "██") -> list[list[str]]:
    rows = height * 2 + 1
    cols = width * 2 + 1
    grid: list[list[str]] = [
        [walls_color + wall_char + end_color] * (cols) for _ in range(rows)]
    for row in range(height):
        for col in range(width):
            cell = maze[row][col]
            cr: int = row * 2 + 1
            cc: int = col * 2 + 1
            grid[cr][cc] = '  '
            if cr == entry[1] * 2 + 1 and cc == entry[0] * 2 + 1:
                grid[cr][cc] = entry_color + 'EN' + end_color
            elif cr == exit_pos[1] * 2 + 1 and cc == exit_pos[0] * 2 + 1:
                grid[cr][cc] = exit_color + 'EX' + end_color
            if not cell['N']:
                grid[cr - 1][cc] = '  '
            if not cell['S']:
                grid[cr + 1][cc] = '  '
            if not cell['E']:
                grid[cr][cc + 1] = '  '
            if not cell['W']:
                grid[cr][cc - 1] = '  '
    grid_print(grid, width, height)
    maze_controle()
    return grid


def print_path(solution: str | None, entry: tuple[int, int], grid: list[list[str]], width: int, height: int, path_color: str, path_char: str = "▓▓") -> None:
    if solution:
        cr: int = entry[1] * 2 + 1
        cc: int = entry[0] * 2 + 1
        for move in solution:
            grid[cr][cc] = path_color + path_char + end_color
            if cr == entry[1] * 2 + 1 and cc == entry[0] * 2 + 1:
                grid[cr][cc] = entry_color + 'EN' + end_color
            if move == 'N':
                grid[cr - 1][cc] = path_color + path_char + end_color
                cr -= 2
            elif move == 'S':
                grid[cr + 1][cc] = path_color + path_char + end_color
                cr += 2
            elif move == 'E':
                grid[cr][cc + 1] = path_color + path_char + end_color
                cc += 2
            elif move == 'W':
                grid[cr][cc - 1] = path_color + path_char + end_color
                cc -= 2
            else:
                print("Error: Invalid path")
                exit(1)
    grid_print(grid, width, height)
    maze_controle()


def welcom() -> None:
    welcom_messg: list[str] = [
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
        "╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝"
    ]
    os.system("clear")
    cols, rows = os.get_terminal_size()
    spaces: int = (cols - 116) // 2
    new_lines: int = (rows - 20) // 2
    print("\n" * new_lines)
    for _ in welcom_messg:
        print(REDDARK_color + motion_color + " " * spaces + _ + RST_color)
    print(GRN_color + motion_color + ((" " * 46) + " " * spaces) +
          "Press 'S' to START!!" + RST_color)

def maze_controle() -> None:
    cols, _ = os.get_terminal_size()
    spaces: int = (cols - 116) // 2
    print("\n" * 3)
    print(((" " * 30) + " " * spaces) + "PRESS : "'\033[31m' + "(Q,q) to QUIT " + '\033[0m' + "; (R,r) to regenerate ; (P,p) to Show PATH")


def wall_path_colors() -> tuple[str, str]:
    colors: dict[str, str] = {
        'WHITE': '\033[0m',
        'RED': '\033[31m',
        'ORANGE': '\033[91m',
        'GRN': '\033[92m',
        'YLW': '\033[93m',
        'BLUE': '\033[94m',
        'PURPLE': '\033[95m',
        'SKYBLUE': '\033[96m',
    }

    def _get_key() -> str:
        chosen: str = ""
        while True:
            char = get_char()
            if char in ['Q', 'q']:
                exit(0)
            elif char in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                if char == '1':
                    chosen = colors['WHITE']
                elif char == '2':
                    chosen = colors['RED']
                elif char == '3':
                    chosen = colors['ORANGE']
                elif char == '4':
                    chosen = colors['GRN']
                elif char == '5':
                    chosen = colors['YLW']
                elif char == '6':
                    chosen = colors['BLUE']
                elif char == '7':
                    chosen = colors['PURPLE']
                elif char == '8':
                    chosen = colors['SKYBLUE']
                elif char == '9':
                    tmp: str = random.choice(list(colors))
                    chosen = colors[tmp]
                break
        return chosen

    def _middel_print(message: str) -> None:
        RESET: str = '\033[0m'
        cols, _ = os.get_terminal_size()
        spaces: int = (cols - 116) // 2
        print(((" " * 40) + " " * spaces) +
              message + RESET)

    def _choose_color() -> None:
        k = 1
        for i in colors:
            _middel_print(" " * 5 + colors[i] + f"{k} - " + i)
            k += 1
        _middel_print(" " * 5 + colors['ORANGE'] + "9 - " +
                    colors['WHITE'] +
                    colors['RED'] + "R" +
                    colors['ORANGE'] + "A" +
                    colors['GRN'] + "N" + 
                    colors['YLW'] + "D" +
                    colors['BLUE'] + "O" +
                    colors['PURPLE'] + "M")

    path: str = ""
    walls: str = ""
    _middel_print("whish color would u like for the walls:")
    _choose_color()
    walls = _get_key()
    _middel_print("Selected walls color is " + walls + "██\n")
    _middel_print("whish color would u like for the path:")
    _choose_color()
    path = _get_key()
    _middel_print("Selected path color is " + path + "██\n")
    time.sleep(1)
    return (walls, path)


def main() -> None:
    colorado: list[str] = ['\033[0m','\033[31m','\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m']
    emoji: list[str] = [ '██', '42', '$$', '@@', '##', '🌲', '🍄', '🪨', '🔥', '🐭', '🐾', '🌟', '🍬', '💎', '🔮', '🫧', '🍪', '👣', '▓▓', '42', '@@']

    w: int = -1
    wc: int = -1
    p: int = -1
    pc: int = -1
    wall_char: str = ""
    path_char: str = ""
    wall_color: str = ""
    path_color: str = ""
    welcom()
    while True:
        path: bool = False
        char: str = get_char()
        if char in ['S', 's']:
            os.system("clear")
            config = parse_config("config.txt")
            gen = MazeGenerator(
                width=config['width'],
                height=config['height'],
                entry=config['entry'],
                exit=config['exit'],
                output_file=config['output_file'],
                perfect=config['perfect'],
                seed=config['seed']
            )
            gen.generate()
            wc += 1
            wall_char = emoji[wc % len(emoji)]
            grid = print_maze(
                wall_char=wall_char,
                walls_color=wall_color,
                maze=gen.maze(),
                width=config['width'],
                height=config['height'],
                entry=config['entry'],
                exit_pos=config['exit']
            )
            while True:
                char = get_char()
                if char in ['R', 'r']:
                    config = parse_config("config.txt")
                    gen = MazeGenerator(
                        width=config['width'],
                        height=config['height'],
                        entry=config['entry'],
                        exit=config['exit'],
                        output_file=config['output_file'],
                        perfect=config['perfect'],
                        seed=config['seed']
                    )
                    gen.generate()
                    wc += 1
                    wall_char = emoji[wc % len(emoji)]
                    grid = print_maze(
                        wall_char=wall_char,
                        walls_color=wall_color,
                        maze=gen.maze(),
                        width=config['width'],
                        height=config['height'],
                        entry=config['entry'],
                        exit_pos=config['exit']
                    )
                    path = False
                elif char in ['P', 'p']:
                    if not path:
                        pc += 1
                        path_char = emoji[pc % len(emoji)]
                        print_path(
                            path_char=path_char,
                            path_color=path_color,
                            solution=gen.solution(),
                            entry=config['entry'],
                            grid=grid,
                            width=config['width'],
                            height=config['height']
                        )
                        path = True
                    else:
                        grid = print_maze(

                            walls_color=wall_color,
                            maze=gen.maze(),
                            width=config['width'],
                            height=config['height'],
                            entry=config['entry'],
                            exit_pos=config['exit']
                        )
                        path = False
                elif char == '1':
                    w += 1
                    wall_color = colorado[(w + 1) % len(colorado)]
                    grid = print_maze(
                            walls_color=wall_color,
                            maze=gen.maze(),
                            width=config['width'],
                            height=config['height'],
                            entry=config['entry'],
                            exit_pos=config['exit']
                        )
                    if path:
                        print_path(
                                path_color=path_color,
                                solution=gen.solution(),
                                entry=config['entry'],
                                grid=grid,
                                width=config['width'],
                                height=config['height']
                            )
                elif char == '2':
                    p += 1
                    path_color = colorado[(p + 1) % len(colorado)]
                    if path:
                        print_path(
                                path_color=path_color,
                                solution=gen.solution(),
                                entry=config['entry'],
                                grid=grid,
                                width=config['width'],
                                height=config['height']
                            )
                # elif char == '3':

                elif char in ['Q', 'q']:
                    exit(0)
        elif char in ['Q', 'q']:
            exit(0)


def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


if __name__ == '__main__':
    main()
