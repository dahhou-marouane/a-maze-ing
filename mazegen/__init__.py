from typing import List, Dict, Tuple
import random
from collections import deque


MOVE: Dict[str, Tuple[int, int]] = {
    'N': (-1,  0),
    'S': (1,  0),
    'E': (0,  1),
    'W': (0, -1)
}

OPPOSITE: Dict[str, str] = {
    'N': 'S',
    'S': 'N',
    'E': 'W',
    'W': 'E'
}

DIGIT_GLYPHS = {
    '4': [
        [1, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 0, 1],
        [0, 0, 1],
    ],
    '2': [
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 1],
        [1, 0, 0],
        [1, 1, 1],
    ],
}
class MazeGenerator:

    def __init__(self,
                 width: int = 20,
                 height: int = 20,
                 entry: Tuple[int, int] = (0, 0),
                 exit: Tuple[int, int]= (19, 19),
                 perfect: bool = True,
                 seed: str | None = None
                 ) -> None:
        """Store the parametres of the maze and init empty maze"""
        self._width: int = width
        self._height: int = height
        self._entry: Tuple[int, int] = entry
        self._exit_pos: Tuple[int, int] = exit
        self._perfect: bool = perfect
        self._seed: str | None = seed
        self._maze: List[List[Dict[str, bool]]] = []
        self._solution: str = ""
        self._cells: set

    def solution(self) -> str:
        return self._solution

    def maze(self) -> List[List[Dict[str, bool]]]:
        return self._maze

    def generate(self) -> None:
        """Generate the maze with DFS algo"""
        random.seed(self._seed)
        self._maze = self._create_maze()
        self._cells = self._get_42_cells()
        self._dfs_algo()
        if not self._perfect:
            self._break_more_walls()
        self._solution = self._find_path()

    def _get_42_cells(self) -> set:
        """Return set of (row, col) that form the '42' digits, centered in the maze."""
        total_w = 7  # 3 + 1 gap + 3
        total_h = 5
        start_row = (self._height - total_h) // 2
        start_col = (self._width  - total_w) // 2

        cells = set()
        for digit, col_offset in [('4', 0), ('2', 4)]:
            for r, row_bits in enumerate(DIGIT_GLYPHS[digit]):
                for c, bit in enumerate(row_bits):
                    if bit:
                        cells.add((start_row + r, start_col + col_offset + c))
        return cells

    def _create_maze(self) -> List[List[Dict[str, bool]]]:
        """Create maze with all the walls closed"""
        maze: List[List[Dict[str, bool]]] = []
        for _ in range(self._height):
            row: List[Dict[str, bool]] = []
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
        """Function of dfs_algo to generate the maze by DFS algo using seed
            and it calls the function open_walls to open the walls for the cell
            and it neigbor"""


        visited: List[List[bool]] = [
            [False] * self._width for _ in range(self._height)]
        for (r, c) in self._cells:
            visited[r][c] = True
        stack: List[Tuple[int, int]] = [(0, 0)]
        visited[0][0] = True
        while stack:
            row, col = stack[-1]
            neigbors: List[Tuple[int, int, str]] = []
            for direcction in ['N', 'E', 'S', 'W']:
                dr, dc = MOVE[direcction]
                next_row = row + dr
                next_col = col + dc
                if (0 <= next_row < self._height and
                        0 <= next_col < self._width and not
                        visited[next_row][next_col]):
                    neigbors.append((next_row, next_col, direcction))
            if neigbors:
                next_row, next_col, direcction = random.choice(neigbors)
                stack.append((next_row, next_col))
                visited[next_row][next_col] = True
                self._open_walls(row, col, direcction)
            else:
                stack.pop()

    def _break_more_walls(self) -> None:
        """This function is called after after dfs_algo fuction if the maze
            should not be prefect to break extra walls"""
        wallstobreak: int = int((self._width * self._height) * 0.15)
        breaked: int = 0
        visited: List[List[bool]] = [
            [False] * self._width for _ in range(self._height)]
        for (r, c) in self._cells:
            visited[r][c] = True
        while breaked < wallstobreak:
            row: int = random.randint(0, self._height - 1)
            col: int = random.randint(0, self._width - 1)
            direction: str = random.choice(['N', 'E', 'S', 'W'])
            dr, dc = MOVE[direction]
            next_row = row + dr
            next_col = col + dc
            if not (0 <= next_row < self._height and
                    0 <= next_col < self._width):
                continue
            if visited[row][col]:
                continue
            if visited[next_row][next_col]:
                continue
            if self._maze[row][col][direction] is False:
                continue
            self._open_walls(row, col, direction)
            breaked += 1

    def _find_path(self) -> str:
        """Find shortest path from entry to exit using BFS algo.
        Returns:
            Path string of N/E/S/W characters e.g. 'NNEESS'
        """
        entryc: int = self._entry[0]
        entryr: int = self._entry[1]
        exitc: int = self._exit_pos[0]
        exitr: int = self._exit_pos[1]
        visited: List[List[bool]] = [
            [False] * self._width for _ in range(self._height)]
        queue: deque[Tuple[int, int, str]] = deque()
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
