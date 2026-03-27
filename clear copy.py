import random
DIGITS: dict[str, list[str]] = {
    '4': [
        "1 0 0",
        "1 0 0",
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
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit_pos: tuple[int, int] = exit
        self.output_file: str = output_file
        self.perfect: bool = perfect
        self.seed: str | None = seed
        self.maze: list[list[dict[str, bool]]] = []
        self.solution: str = ""

    def generate(self) -> list[list[dict[str, bool]]]:
        """Generate the maze with DFS algo"""
        random.seed(self.seed)
        self.maze = self._create_maze()
        self._stamp_42()
        self._dfs_algo()
        if not self.perfect:
            self._break_more_walls()
        self.solution = self._find_path()
        return self.maze

    def _create_maze(self) -> list[list[dict[str, bool]]]:
        """Create maze with all the walls closed"""
        maze: list[list[dict[str, bool]]] = []
        for _ in range(self.height):
            row: list[dict[str, bool]] = []
            for _ in range(self.width):
                cell = {'N': True, 'E': True, 'S': True, 'W': True}
                row.append(cell)
            maze.append(row)
        return maze

    def _open_walls(self, row: int, col: int, direction: str) -> None:
        """Open wall between cell and neighbor cell"""
        self.maze[row][col][direction] = False
        dr, dc = MOVE[direction]
        next_row = row + dr
        next_col = col + dc
        self.maze[next_row][next_col][OPPOSITE[direction]] = False


    def _stamp_42(self) -> None:
        digit_rows, digit_cols, gap = 5, 3, 1
        total_cols = digit_cols + gap + digit_cols
        scale_r = max(1, (self.height // 2) // digit_rows)
        scale_c = max(1, (self.width  // 2) // digit_cols)
        scale   = min(scale_r, scale_c)
        stamped_rows = digit_rows * scale
        stamped_cols = total_cols * scale
        start_r = (self.height - stamped_rows) // 2
        start_c = (self.width  - stamped_cols) // 2

        pixels = [[0]*stamped_cols for _ in range(stamped_rows)]
        for digit_i, digit_char in enumerate(['4','2']):
            col_offset = digit_i * (digit_cols + gap) * scale
            for pr, row_str in enumerate(DIGITS[digit_char]):
                for pc, bit in enumerate(row_str.split()):
                    if bit == '1':
                        for sr in range(scale):
                            for sc in range(scale):
                                pixels[pr*scale+sr][pc*scale+sc+col_offset] = 1

        self.stamped: set[tuple[int,int]] = set()   # ← track stamped cells
        for dr in range(stamped_rows):
            for dc in range(stamped_cols):
                if pixels[dr][dc] == 1:
                    r, c = start_r+dr, start_c+dc
                    if 0 <= r < self.height and 0 <= c < self.width:
                        self.stamped.add((r, c))    # ← record it

    def _dfs_algo(self) -> None:
        visited = [[False]*self.width for _ in range(self.height)]
        for r, c in self.stamped:                   # ← use the set, not wall state
            visited[r][c] = True

        start = next(
            ((r,c) for r in range(self.height) for c in range(self.width) if not visited[r][c]),
            None
        )
        if not start:
            return

        stack = [start]
        visited[start[0]][start[1]] = True
        while stack:
            row, col = stack[-1]
            neighbors = []
            for d in ['N','E','S','W']:
                dr, dc = MOVE[d]
                nr, nc = row+dr, col+dc
                if 0 <= nr < self.height and 0 <= nc < self.width and not visited[nr][nc]:
                    neighbors.append((nr, nc, d))
            if neighbors:
                nr, nc, d = random.choice(neighbors)
                stack.append((nr, nc))
                visited[nr][nc] = True
                self._open_walls(row, col, d)
            else:
                stack.pop()

    def _break_more_walls(self) -> None:
        wallstobreak = int((self.width * self.height) * 0.15)
        breaked = 0
        while breaked < wallstobreak:
            row = random.randint(0, self.height-1)
            col = random.randint(0, self.width-1)
            if (row, col) in self.stamped:          # ← use the set
                continue
            direction = random.choice(['N','E','S','W'])
            dr, dc = MOVE[direction]
            nr, nc = row+dr, col+dc
            if not (0 <= nr < self.height and 0 <= nc < self.width):
                continue
            if (nr, nc) in self.stamped:            # ← use the set
                continue
            if not self.maze[row][col][direction]:
                continue
            self._open_walls(row, col, direction)
            breaked += 1

    def _find_path(self) -> str:
        """Find shortest path from entry to exit using BFS.
        Returns:
            Path string of N/E/S/W characters e.g. 'NNEESS'
        """
        from collections import deque
        start_r: int = self.entry[1]
        start_c: int = self.entry[0]
        goal_r: int  = self.exit_pos[1]
        goal_c: int  = self.exit_pos[0]

        visited: list[list[bool]] = [[False] * self.width for _ in range(self.height)]

        queue: deque[tuple[int, int, str]] = deque()
        queue.append((start_r, start_c, ""))
        visited[start_r][start_c] = True

        while queue:
            row, col, path = queue.popleft()

            # check if reached goal
            if row == goal_r and col == goal_c:
                return path

            # check all 4 directions
            for direction in ['N', 'E', 'S', 'W']:
                # wall must be OPEN
                if not self.maze[row][col][direction]:
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

    if path_cells:
        for (r, c) in path_cells:
            grid[r * 2 + 1][c * 2 + 1] = '\033[93m██\033[0m'

    if solution:
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
        print(''.join(row))


def main() -> None:
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
    for direction in gen.solution:
        path_cells.add((row, col))
        dr, dc = MOVE[direction]
        row += dr
        col += dc
    path_cells.add((row, col))

    print_maze(
        gen.maze,
        config['width'],
        config['height'],
        config['entry'],
        config['exit'],
        path_cells,
        gen.solution
    )

if __name__ == '__main__':
    main()