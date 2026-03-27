import random


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
            print(f"Erropr: missing key [{ky}] in config file") 
            exit(1)
    try:
        width: int = int(config['WIDTH'])
        height: int = int(config['HEIGHT'])

        entry_x, entry_y = config['ENTRY'].split(',')
        exit_x, exit_y = config['EXIT'].split(',')
        
        entry_pos: tuple[int, int] = (int(entry_x), int(entry_y))
        exit_pos: tuple[int, int]= (int(exit_x), int(exit_y))
        if "SEED" not in config or config['SEED'].strip() == "":
            seed: int | None = None
        else:
            seed = int(config['SEED'])
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

def first() -> None:
    print(random.choice(['n', 'e', 's', 'w']))
def second() -> None:
    random.seed(42)
    print(random.choice(['n', 'e', 's', 'w']))
first()
second()
def _find_path(self) -> str:
    """Find shortest path from entry to exit using BFS.

    Returns:
        Path string of N/E/S/W characters e.g. 'NNEESS'
    """
    from collections import deque

    # Step 1 — convert (x,y) to (row, col)
    # remember: entry is (x, y) = (col, row)
    start_row: int = self.entry[1]
    start_col: int = self.entry[0]
    goal_row: int = self.exit_pos[1]
    goal_col: int = self.exit_pos[0]

    # Step 2 — visited grid so we don't go in circles
    visited: list[list[bool]] = [
        [False] * self.width for _ in range(self.height)
    ]
    visited[start_row][start_col] = True

    # Step 3 — queue stores (row, col, path_so_far)
    queue: deque[tuple[int, int, str]] = deque()
    queue.append((start_row, start_col, ""))

    # Step 4 — BFS loop
    while queue:
        row, col, path = queue.popleft()
        if row == goal_row and col == goal_col:
            return path
        for direction in ['N', 'E', 'S', 'W']:

            # can we go this way? wall must be OPEN
            if not self.maze[row][col][direction]:
                dr, dc = MOVE[direction]
                nr = row + dr
                nc = col + dc

                # only visit unvisited cells
                if not visited[nr][nc]:
                    visited[nr][nc] = True
                    queue.append((nr, nc, path + direction))

    # no path found (should never happen in valid maze)
    return ""