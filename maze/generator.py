import random
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
    'S': ( 1,  0),
    'E': ( 0,  1),
    'W': ( 0, -1)
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
        # self.open_all_walls()
        # self._stamp_42()
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

    # for testing remove
    def open_all_walls(self) -> None:
        for row in range(self._height):
            for col in range(self._width):

                # open North if not on top border
                if row > 0:
                    self._maze[row][col]['N'] = False
                    self._maze[row - 1][col]['S'] = False

                # open South if not on bottom border
                if row < self._height - 1:
                    self._maze[row][col]['S'] = False
                    self._maze[row + 1][col]['N'] = False

                # open East if not on right border
                if col < self._width - 1:
                    self._maze[row][col]['E'] = False
                    self._maze[row + 1 - 1][col + 1]['W'] = False

                # open West if not on left border
                if col > 0:
                    self._maze[row][col]['W'] = False
                    self._maze[row][col - 1]['E'] = False

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

        visited: list[list[bool]] = [[False] * self._width for _ in range(self._height)]
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


    def _stamp_42(self) -> None:
        """Stamp '42' as real walls in the center of the maze."""

        digit_rows = 5
        digit_cols = 3
        gap = 1  # gap between '4' and '2'
        total_cols = digit_cols + gap + digit_cols  # 3 + 1 + 3 = 7

        # scale factor so digits fill ~half the maze
        scale_r = min(1, (self._height // 2) // digit_rows)
        scale_c = min(1, (self._width  // 2) // digit_cols)
        scale = 1

        stamped_rows = digit_rows * scale
        stamped_cols = total_cols * scale

        # center offset
        start_r = (self._height - stamped_rows) // 2
        start_c = (self._width  - stamped_cols) // 2

        # build pixel map for '4' then '2' side by side
        pixels: list[list[int]] = [[0] * stamped_cols for _ in range(stamped_rows)]

        for digit_i, digit_char in enumerate(['4', '2']):
            pattern = DIGITS[digit_char]
            col_offset = digit_i * (digit_cols + gap) * scale
            for pr, row_str in enumerate(pattern):
                bits = row_str.split()
                for pc, bit in enumerate(bits):
                    if bit == '1':
                        for sr in range(scale):
                            for sc in range(scale):
                                pixels[pr * scale + sr][pc * scale + sc + col_offset] = 1

        # stamp into maze — close all 4 walls of blocked cells
        for dr in range(stamped_rows):
            for dc in range(stamped_cols):
                if pixels[dr][dc] == 1:
                    r = start_r + dr
                    c = start_c + dc
                    if 0 <= r < self._height and 0 <= c < self._width:
                        # close all walls of this cell
                        for direction in ['N', 'E', 'S', 'W']:
                            self._maze[r][c][direction] = True
                        # also close the neighbor's shared wall
                        for direction, (nr_d, nc_d) in [
                            ('N', (-1, 0)), ('S', (1, 0)),
                            ('E', (0, 1)), ('W', (0, -1))
                        ]:
                            nr, nc = r + nr_d, c + nc_d
                            if 0 <= nr < self._height and 0 <= nc < self._width:
                                self._maze[nr][nc][OPPOSITE[direction]] = True

    def _find_path(self) -> str:
        """Find shortest path from entry to exit using BFS.
        Returns:
            Path string of N/E/S/W characters e.g. 'NNEESS'
        """
        from collections import deque
        start_r: int = self._entry[1]
        start_c: int = self._entry[0]
        goal_r: int  = self._exit_pos[1]
        goal_c: int  = self._exit_pos[0]
        visited: list[list[bool]] = [[False] * self._width for _ in range(self._height)]
        queue: deque[tuple[int, int, str]] = deque()
        print(queue)
        queue.append((start_r, start_c, ""))
        print(queue)
        
        visited[start_r][start_c] = True
        while queue:
            row, col, path = queue.popleft()
            if row == goal_r and col == goal_c:
                return path

            # check all 4 directions
            for direction in ['N', 'E', 'S', 'W']:
                # wall must be OPEN
                if not self._maze[row][col][direction]:
                    dr, dc = MOVE[direction]
                    nr = row + dr
                    nc = col + dc
                    if not visited[nr][nc]:
                        visited[nr][nc] = True
                        queue.append((nr, nc, path + direction))
        return ""



def parse_config(file: str) -> dict[str, int | bool | tuple[int, int] | str | None]:
    """read the config file and validate it and parse it to dict"""
    config: dict[str, int | str] = {}
    keys: list[str] = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
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
        exit_pos: tuple[int, int]= (int(exit_x), int(exit_y))
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


import sys
def print_maze(
    maze: list[list[dict[str, bool]]],
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
    path_cells: set[tuple[int, int]] | None = None,
    solution: str = ""
) -> None:

    rows: int = height * 2 + 1
    cols: int = width * 2 + 1
    grid: list[list[str]] = [['██'] * cols for _ in range(rows)]

    for row in range(height):
        for col in range(width):
            cell = maze[row][col]
            cr: int = row * 2 + 1
            cc: int = col * 2 + 1

            grid[cr][cc] = '  '

            if not cell['N']:
                grid[cr - 1][cc] = '  '
            if not cell['S']:
                grid[cr + 1][cc] = '  '
            if not cell['E']:
                grid[cr][cc + 1] = '  '
            if not cell['W']:
                grid[cr][cc - 1] = '  '
    if solution:
        if path_cells:
            for (r, c) in path_cells:
                grid[r * 2 + 1][c * 2 + 1] = '\033[93m██\033[0m'
        row, col = entry[1], entry[0]
        for direction in solution:
            dr, dc = MOVE[direction]
            wall_r = row * 2 + 1 + dr
            wall_c = col * 2 + 1 + dc
            grid[wall_r][wall_c] = '\033[93m██\033[0m'
            row += dr
            col += dc

    entry_r = entry[1] * 2 + 1
    entry_c = entry[0] * 2 + 1
    exit_r  = exit_pos[1] * 2 + 1
    exit_c  = exit_pos[0] * 2 + 1
    grid[entry_r][entry_c] = '\033[92m██\033[0m'
    grid[exit_r][exit_c]   = '\033[91m██\033[0m'

    for row in grid:
        s = ''.join(row)
        sys.stdout.write(s)
        sys.stdout.write("\n")
        sys.stdout.flush()


def main(i: int) -> None:
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

    path_cells: set[tuple[int, int]] = set()
    row, col = config['entry'][1], config['entry'][0]
    for direction in gen._solution:
        path_cells.add((row, col))
        dr, dc = MOVE[direction]
        row += dr
        col += dc
    path_cells.add((row, col))
    if i:
        print_maze(
            gen.maze(),
            config['width'],
            config['height'],
            config['entry'],
            config['exit'],
            path_cells,
            gen.solution(),
        )
    else:
            print_maze(
            gen.maze(),
            config['width'],
            config['height'],
            config['entry'],
            config['exit'],
            path_cells,
        )

import time
import tty
import termios
def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd) 
        return sys.stdin.read(1) 
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # restore



if __name__ == '__main__':
    import os
    # os.system("clear")
    path = False
    main(0)
    print("\033[91mEXIT 'q'\033[0m    \033[92mREGENERATE 'r'\033[0m    \033[93mSHOW_PATH 'p'\033[0m")
    while True:
        inpu = get_char()
        if inpu in ["q" , 'Q']:
            exit(0)
        elif inpu in ["r", "R"]:
            # os.system("clear")
            main(1)
            print("\033[91mEXIT 'q'\033[0m    \033[92mREGENERATE 'r'\033[0m    \033[93mSHOW_PATH 'p'\033[0m")

            path = False
        elif inpu in ["p", "P"]:
            if path == False:
                # os.system("clear")
                main(1)
                print("\033[91mEXIT 'q'\033[0m    \033[92mREGENERATE 'r'\033[0m    \033[93mSHOW_PATH 'p'\033[0m")
                path = True
