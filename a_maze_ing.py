import select
import tty
import termios
import os
import time
import sys
from typing import cast, List, Dict, Tuple
from mazegen import MazeGenerator


def write_output(output_file: str,
                 maze: List[List[Dict[str, bool]]],
                 width: int,
                 height: int,
                 entry: Tuple[int, int],
                 exit_pos: Tuple[int, int],
                 solution: str) -> None:
    wall_direction: Dict[str, int] = {'N': 1, 'E': 2, 'S': 4, 'W': 8}
    try:
        with open(output_file, "w") as f:
            for row in range(height):
                for col in range(width):
                    sum: int = 0
                    for direction, wall in wall_direction.items():
                        if maze[row][col][direction]:
                            sum += wall
                    f.write(hex(sum)[2:].upper())
                f.write("\n")
            f.write("\n")
            f.write(f"{entry[0]},{entry[1]}\n")
            f.write(f"{exit_pos[0]},{exit_pos[1]}\n")
            f.write(f"{solution}\n")
    except (FileNotFoundError, PermissionError, IsADirectoryError):
        print("s")


def parse_config(
        file: str
) -> Dict[str, int | bool | Tuple[int, int] | str | None]:
    """read the config file and validate it and parse it to dict"""

    def _check_output_file(file: str) -> str:
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
        return output_path

    config: Dict[str, str] = {}
    keys: List[str] = ["WIDTH", "HEIGHT",
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
    return {
        'width': width,
        'height': height,
        'entry': entry_pos,
        'exit': exit_pos,
        'output_file': config['OUTPUT_FILE'],
        'perfect': perfect,
        'seed': seed
    }


def grid_print(
    grid: List[List[str]],
    width: int,
    height: int
) -> None:
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


def print_maze(
    maze: List[List[Dict[str, bool]]],
    width: int,
    height: int,
    entry: Tuple[int, int],
    exit_pos: Tuple[int, int],
    walls_color: str,
    wall_char: str = "██"
) -> List[List[str]]:
    rows = height * 2 + 1
    cols = width * 2 + 1
    grid: List[List[str]] = [
        [walls_color + wall_char + '\033[0m'] * (cols) for _ in range(rows)]
    for row in range(height):
        for col in range(width):
            cell = maze[row][col]
            cr: int = row * 2 + 1
            cc: int = col * 2 + 1
            grid[cr][cc] = '  '
            if cr == entry[1] * 2 + 1 and cc == entry[0] * 2 + 1:
                grid[cr][cc] = '\033[102m' + 'EN' + '\033[0m'
            elif cr == exit_pos[1] * 2 + 1 and cc == exit_pos[0] * 2 + 1:
                grid[cr][cc] = '\033[101m' + 'EX' + '\033[0m'
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


def print_path(
    solution: str | None,
    entry: Tuple[int, int],
    grid: List[List[str]],
    width: int, height: int,
    path_color: str,
    path_char: str = "▓▓"
) -> None:
    if solution:
        cr: int = entry[1] * 2 + 1
        cc: int = entry[0] * 2 + 1
        for move in solution:
            grid[cr][cc] = path_color + path_char + '\033[0m'
            if cr == entry[1] * 2 + 1 and cc == entry[0] * 2 + 1:
                grid[cr][cc] = '\033[102m' + 'EN' + '\033[0m'
            if move == 'N':
                grid[cr - 1][cc] = path_color + path_char + '\033[0m'
                cr -= 2
            elif move == 'S':
                grid[cr + 1][cc] = path_color + path_char + '\033[0m'
                cr += 2
            elif move == 'E':
                grid[cr][cc + 1] = path_color + path_char + '\033[0m'
                cc += 2
            elif move == 'W':
                grid[cr][cc - 1] = path_color + path_char + '\033[0m'
                cc -= 2
            else:
                print("Error: Invalid path")
                exit(1)
    grid_print(grid, width, height)
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
    os.system("clear")
    cols, rows = os.get_terminal_size()
    spaces: int = (cols - 116) // 2
    new_lines: int = (rows - 20) // 2
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

def handel_exit() -> None:
    pass

def redraw(
    path: bool,
    gen: MazeGenerator,
    grid: List[List[str]],
    config: Dict[str, int | bool | Tuple[int, int] | str | None],
    wall_char: str,
    wall_color: str,
    path_char: str,
    path_color: str) -> None:
    if path:
        print_path(
            path_char=path_char,
            path_color=path_color,
            solution=gen.solution(),
            entry=cast(Tuple[int, int], config['entry']),
            grid=grid,
            width=cast(int, config['width']),
            height=cast(int, config['height'])
        )
    else:
        print_maze(
            wall_char=wall_char,
            walls_color=wall_color,
            maze=gen.maze(),
            width=cast(int, config['width']),
            height=cast(int, config['height']),
            entry=cast(Tuple[int, int], config['entry']),
            exit_pos=cast(Tuple[int, int], config['exit'])
        )

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

    def _check_terminal() -> Tuple[int, int]:
        new_col, new_rows = os.get_terminal_size()
        if (old_col, old_rows) != (new_col, new_rows):
            redraw(path=path,
                   gen=gen,
                   grid=grid,
                   config=config,
                   wall_char=wall_char,
                   wall_color=wall_color,
                   path_char=path_char,
                   path_color=path_color)
        return (new_col, new_rows)

    if len(sys.argv) == 1:
        print("Error: The program must be run with the following command:\n"
              "python3 a_maze_ing.py [config_file_here]")
        exit(1)
    config_file: str = sys.argv[1]
    welcom()
    while True:
        char: str = get_char()
        if char in ['S', 's']:
            os.system("clear")
            config = parse_config(config_file)
            gen = MazeGenerator(
                width=cast(int, config['width']),
                height=cast(int, config['height']),
                entry=cast(Tuple[int, int], config['entry']),
                exit=cast(Tuple[int, int], config['exit']),
                output_file=cast(str, config['output_file']),
                perfect=cast(bool, config['perfect']),
                seed=cast(str | None, config['seed'])
            )
            gen.generate()
            write_output(output_file=cast(str, config['output_file']),
                         maze=gen.maze(),
                         width=cast(int, config['width']),
                         height=cast(int, config['height']),
                         entry=cast(Tuple[int, int], config['entry']),
                         exit_pos=cast(Tuple[int, int], config['exit']),
                         solution=gen.solution())
            grid = print_maze(
                wall_char=wall_char,
                walls_color=wall_color,
                maze=gen.maze(),
                width=cast(int, config['width']),
                height=cast(int, config['height']),
                entry=cast(Tuple[int, int], config['entry']),
                exit_pos=cast(Tuple[int, int], config['exit'])
            )
            while True:
                char = get_char()
                old_col, old_rows = _check_terminal()
                if char in ['R', 'r']:
                    config = parse_config(config_file)
                    gen = MazeGenerator(
                        width=cast(int, config['width']),
                        height=cast(int, config['height']),
                        entry=cast(Tuple[int, int], config['entry']),
                        exit=cast(Tuple[int, int], config['exit']),
                        output_file=cast(str, config['output_file']),
                        perfect=cast(bool, config['perfect']),
                        seed=cast(str | None, config['seed'])
                    )
                    gen.generate()
                    grid = print_maze(
                        wall_char=wall_char,
                        walls_color=wall_color,
                        maze=gen.maze(),
                        width=cast(int, config['width']),
                        height=cast(int, config['height']),
                        entry=cast(Tuple[int, int], config['entry']),
                        exit_pos=cast(Tuple[int, int], config['exit'])
                    )
                    path = False
                elif char in ['P', 'p']:
                    if not path:
                        print_path(
                            path_char=path_char,
                            path_color=path_color,
                            solution=gen.solution(),
                            entry=cast(Tuple[int, int], config['entry']),
                            grid=grid,
                            width=cast(int, config['width']),
                            height=cast(int, config['height'])
                        )
                        path = True
                    else:
                        grid = print_maze(
                            wall_char=wall_char,
                            walls_color=wall_color,
                            maze=gen.maze(),
                            width=cast(int, config['width']),
                            height=cast(int, config['height']),
                            entry=cast(Tuple[int, int], config['entry']),
                            exit_pos=cast(Tuple[int, int], config['exit'])
                        )
                        path = False
                elif char == '1':
                    w += 1
                    wall_color = colorado[(w + 1) % len(colorado)]
                    grid = print_maze(
                        wall_char=wall_char,
                        walls_color=wall_color,
                        maze=gen.maze(),
                        width=cast(int, config['width']),
                        height=cast(int, config['height']),
                        entry=cast(Tuple[int, int], config['entry']),
                        exit_pos=cast(Tuple[int, int], config['exit'])
                    )
                    if path:
                        print_path(
                            path_char=path_char,
                            path_color=path_color,
                            solution=gen.solution(),
                            entry=cast(Tuple[int, int], config['entry']),
                            grid=grid,
                            width=cast(int, config['width']),
                            height=cast(int, config['height'])
                        )
                elif char == '2':
                    p += 1
                    path_color = colorado[(p + 1) % len(colorado)]
                    if path:
                        print_path(
                            path_char=path_char,
                            path_color=path_color,
                            solution=gen.solution(),
                            entry=cast(Tuple[int, int], config['entry']),
                            grid=grid,
                            width=cast(int, config['width']),
                            height=cast(int, config['height'])
                        )
                elif char == '3':
                    wc += 1
                    wall_char = emoji[(wc + 1) % len(emoji)]
                    grid = print_maze(
                        wall_char=wall_char,
                        walls_color=wall_color,
                        maze=gen.maze(),
                        width=cast(int, config['width']),
                        height=cast(int, config['height']),
                        entry=cast(Tuple[int, int], config['entry']),
                        exit_pos=cast(Tuple[int, int], config['exit'])
                    )
                    if path:
                        print_path(
                            path_char=path_char,
                            path_color=path_color,
                            solution=gen.solution(),
                            entry=cast(Tuple[int, int], config['entry']),
                            grid=grid,
                            width=cast(int, config['width']),
                            height=cast(int, config['height'])
                        )
                elif char == '4':
                    pc += 1
                    path_char = emoji2[(pc + 1) % len(emoji2)]
                    if path:
                        print_path(
                            path_char=path_char,
                            path_color=path_color,
                            solution=gen.solution(),
                            entry=cast(Tuple[int, int], config['entry']),
                            grid=grid,
                            width=cast(int, config['width']),
                            height=cast(int, config['height'])
                        )
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
                            if path:
                                print_path(
                                    path_char=path_char,
                                    path_color=path_color,
                                    solution=gen.solution(),
                                    entry=cast(Tuple[int, int],
                                               config['entry']),
                                    grid=grid,
                                    width=cast(int, config['width']),
                                    height=cast(int, config['height'])
                                )
                            else:
                                grid = print_maze(
                                    wall_char=wall_char,
                                    walls_color=wall_color,
                                    maze=gen.maze(),
                                    width=cast(int, config['width']),
                                    height=cast(int, config['height']),
                                    entry=cast(Tuple[int, int],
                                               config['entry']),
                                    exit_pos=cast(
                                        Tuple[int, int], config['exit'])
                                )
                            break
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
                    welcom()
                    break


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
    main()
