import select
import tty
import termios
import os
import time
import sys
from typing import List, Dict, Tuple
from mazegen import MazeGenerator

class AllData:
    colorado: List[str] = ['\033[0m', '\033[31m', '\033[91m',
                           '\033[92m', '\033[93m', '\033[94m',
                           '\033[95m', '\033[96m']
    emoji: List[str] = ['██', '42', '$$', '@@', '##', '🌲', '🍄', '🔥']
    emoji2: List[str] = ['▓▓', '🐭', '🐾', '🌟',
                         '🍬', '💎', '🔮', '🍪', '👣', '42', '@@']
    w: int = -1
    wc: int = -1
    p: int = -1
    pc: int = -1
    wall_char: str = emoji[0]
    path_char: str = emoji2[0]
    wall_color: str = ""
    path_color: str = ""
    old_col: int = 0
    old_rows: int = 0
    path: bool = False
    gen: MazeGenerator = MazeGenerator()
    width: int
    height: int
    entry: Tuple[int, int]
    exit_pos: Tuple[int, int]
    perfect: bool
    seed: str | None
    grid: List[List[str]]
    maze: List[List[Dict[str, bool]]] = gen.maze()
    solution: str = gen.solution()
    output_file: str
    config_file: str = ""
    def regenerate(self) -> None:
        self.gen = MazeGenerator(
                width=self.width,
                height=self.height,
                entry=self.entry,
                exit=self.exit_pos,
                perfect=self.perfect,
                seed=self.seed
                )
        self.gen.generate()
        self.maze = self.gen.maze()
        self.solution = self.gen.solution()
        write_output(self)

def write_output(data: AllData) -> None:
    wall_direction: Dict[str, int] = {'N': 1, 'E': 2, 'S': 4, 'W': 8}
    try:
        with open(data.output_file, "w") as f:
            for row in range(data.height):
                for col in range(data.width):
                    sum: int = 0
                    for direction, wall in wall_direction.items():
                        if data.maze[row][col][direction]:
                            sum += wall
                    f.write(hex(sum)[2:].upper())
                f.write("\n")
            f.write("\n")
            f.write(f"{data.entry[0]},{data.entry[1]}\n")
            f.write(f"{data.exit_pos[0]},{data.exit_pos[1]}\n")
            f.write(f"{data.solution}\n")
    except (FileNotFoundError, PermissionError, IsADirectoryError):
        print("s")


def parse_config(data: AllData) -> None:
    """read the config file and validate it and parse it to dict"""
    data.config_file = sys.argv[1]
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
                       "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    try:
        with open(data.config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    raise ValueError(f"Bad config line [{line}]")
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    except (FileNotFoundError, IsADirectoryError,
            PermissionError, ValueError) as e:
        print("Error:", e)
        exit(1)
    for ky in keys:
        if ky not in config:
            print(f"Error: missing key [{ky}] in config file")
            exit(1)
    try:
        width: int = int(config['WIDTH'])
        height: int = int(config['HEIGHT'])

        entry_x, entry_y = config['ENTRY'].strip("() ").split(',')
        exit_x, exit_y = config['EXIT'].strip("() ").split(',')

        entry_pos: Tuple[int, int] = (int(entry_x), int(entry_y))
        exit_pos: Tuple[int, int] = (int(exit_x), int(exit_y))
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
    _check_output_file(config['OUTPUT_FILE'])
    data.width = width
    data.height = height
    data.entry = entry_pos
    data.exit_pos = exit_pos
    data.output_file = config['OUTPUT_FILE']
    data.perfect = perfect
    data.seed = seed


def grid_print(data: AllData) -> None:
    cols, rows = os.get_terminal_size()
    if cols < (data.width * 2 + 1) * 2 + 1  or rows < data.height * 2 + 12:
        os.system("clear")
        middel_print("Terminal is small to print the maze")
        return
    spaces: int = (cols - (data.width * 2 + 1) * 2) // 2
    new_lines: int = (rows - (data.height * 2 + 1)) // 2
    os.system("clear")
    print("\n" * new_lines)
    for _ in data.grid:
        print(" " * spaces, end="")
        for i in _:
            print(i, end="")
        print()


def print_maze(data: AllData) -> None:
    rows: int = data.height * 2 + 1
    cols: int = data.width * 2 + 1
    data.grid = [[data.wall_color + data.wall_char + '\033[0m'] * (cols) for _ in range(rows)]
    for row in range(data.height):
        for col in range(data.width):
            cell = data.maze[row][col]
            cr: int = row * 2 + 1
            cc: int = col * 2 + 1
            data.grid[cr][cc] = '  '
            if cr == data.entry[1] * 2 + 1 and cc == data.entry[0] * 2 + 1:
                data.grid[cr][cc] = '\033[102m' + 'EN' + '\033[0m'
            elif cr == data.exit_pos[1] * 2 + 1 and cc == data.exit_pos[0] * 2 + 1:
                data.grid[cr][cc] = '\033[101m' + 'EX' + '\033[0m'
            if not cell['N']:
                data.grid[cr - 1][cc] = '  '
            if not cell['S']:
                data.grid[cr + 1][cc] = '  '
            if not cell['E']:
                data.grid[cr][cc + 1] = '  '
            if not cell['W']:
                data.grid[cr][cc - 1] = '  '
    grid_print(data=data)
    maze_controle()



def print_path(data: AllData) -> None:
    if data.solution:
        cr: int = data.entry[1] * 2 + 1
        cc: int = data.entry[0] * 2 + 1
        for move in data.solution:
            data.grid[cr][cc] = data.path_color + data.path_char + '\033[0m'
            if cr == data.entry[1] * 2 + 1 and cc == data.entry[0] * 2 + 1:
                data.grid[cr][cc] = '\033[102m' + 'EN' + '\033[0m'
            if move == 'N':
                data.grid[cr - 1][cc] = data.path_color + data.path_char + '\033[0m'
                cr -= 2
            elif move == 'S':
                data.grid[cr + 1][cc] = data.path_color + data.path_char + '\033[0m'
                cr += 2
            elif move == 'E':
                data.grid[cr][cc + 1] = data.path_color + data.path_char + '\033[0m'
                cc += 2
            elif move == 'W':
                data.grid[cr][cc - 1] = data.path_color + data.path_char + '\033[0m'
                cc -= 2
            else:
                print("Error: Invalid path")
                exit(1)
    grid_print(data=data)
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
            


def redraw(data: AllData) -> None:
    if data.path:
        print_path(data=data)
    else:
        print_maze(data=data)


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
    data: AllData = AllData()

    def _check_terminal(is_welcom: bool = False) -> Tuple[int, int]:
        new_col, new_rows = os.get_terminal_size()
        if (data.old_col, data.old_rows) != (new_col, new_rows):
            if is_welcom:
                welcom()
                return (new_col, new_rows)
            redraw(data=data)
        return (new_col, new_rows)

    if len(sys.argv) == 1:
        print("Error: The program must be run with the following command:\n"
              "python3 a_maze_ing.py [config_file_here]")
        exit(1)
    welcom()
    while True:
        char: str = get_char()
        data.old_col, data.old_rows = _check_terminal(True)
        if char in ['S', 's']:
            os.system("clear")
            parse_config(data=data)
            data.regenerate()
            write_output(data=data)
            print_maze(data=data)
            while True:
                char = get_char()
                data.old_col, data.old_rows = _check_terminal()
                if char in ['R', 'r']:
                    parse_config(data=data)
                    data.regenerate()
                    print_maze(data=data)
                    data.path = False
                elif char in ['P', 'p']:
                    if not data.path:
                        print_path(data=data)
                        data.path = True
                    else:
                        print_maze(data=data)
                        data.path = False
                elif char == '1':
                    data.w += 1
                    data.wall_color = data.colorado[(data.w + 1) % len(data.colorado)]
                    print_maze(data=data)
                    if data.path:
                        print_path(data=data)
                elif char == '2':
                    data.p += 1
                    data.path_color = data.colorado[(data.p + 1) % len(data.colorado)]
                    if data.path:
                        print_path(data=data)
                elif char == '3':
                    data.wc += 1
                    data.wall_char = data.emoji[(data.wc + 1) % len(data.emoji)]
                    print_maze(data=data)
                    if data.path:
                        print_path(data=data)
                elif char == '4':
                    data.pc += 1
                    data.path_char = data.emoji2[(data.pc + 1) % len(data.emoji2)]
                    if data.path:
                        print_path(data=data)
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
                            if data.path:
                                print_path(data=data)
                            else:
                                print_maze(data=data)
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
