from typing import List, Dict, Tuple
import random
from collections import deque

MOVE: Dict[str, Tuple[int, int]] = {
    "N": (-1, 0),
    "S": (1, 0),
    "E": (0, 1),
    "W": (0, -1),
}

OPPOSITE: Dict[str, str] = {"N": "S", "S": "N", "E": "W", "W": "E"}


class MazeGenerator:
    """Generates a 2D maze using iterative DFS.
    Carves passages through a fully-walled grid. Supports perfect mazes
    (unique path between any two cells) and imperfect ones with extra loops.
    On grids ≥(9,9), embeds a "42" pixel-art that DFS carves around.

    Example usage:
        from mazegen.generator import MazeGenerator

        gen = MazeGenerator(
            width=20,
            height=15,
            entry=(0, 0),
            exit=(19, 14),
            perfect=True,
            seed="42"
        )

        gen.generate()

        maze = gen.maze()
        solution = gen.solution()
    """

    def __init__(
        self,
        width: int = 20,
        height: int = 20,
        entry: Tuple[int, int] = (0, 0),
        exit: Tuple[int, int] = (19, 19),
        perfect: bool = True,
        seed: str | None = None,
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
        self._stamp: List[Tuple[int, int]] = []

    def solution(self) -> str:
        """Returns the shortest path from entry to exit
        as 'N;E;S;W' characters."""
        return self._solution

    def maze(self) -> List[List[Dict[str, bool]]]:
        """Returns the maze grid.

        Returns:
            A 2D list of cell dicts mapping direction → wall present (bool).
        """
        return self._maze

    def generate(self) -> None:
        """Builds the maze and computes its solution.

        Initialises the grid, runs DFS, optionally breaks extra
        walls if imprefect maze, then stores the BFS shortest
        path in ``_solution``.
        """
        random.seed(self._seed)
        self._maze = self._create_maze()
        self._dfs_algo()
        if not self._perfect:
            self._break_more_walls()
        self._solution = self._find_path()

    def _create_maze(self) -> List[List[Dict[str, bool]]]:
        """Calculate a (height * width) grid with all walls intact.

        Returns:
            Grid where every cell dict has 'N;E;S;W' all set to True.
        """
        maze: List[List[Dict[str, bool]]] = []
        for _ in range(self._height):
            row: List[Dict[str, bool]] = []
            for _ in range(self._width):
                cell = {"N": True, "E": True, "S": True, "W": True}
                row.append(cell)
            maze.append(row)
        return maze

    def _open_walls(self, row: int, col: int, direction: str) -> None:
        """Removes the shared wall between a cell and its neighbour.

        Args:
            row: Row index of the source cell.
            col: Column index of the source cell.
            direction: Direction toward the neighbour ('N', 'E', 'S', or 'W').
        """
        self._maze[row][col][direction] = False
        dr, dc = MOVE[direction]
        next_row = row + dr
        next_col = col + dc
        self._maze[next_row][next_col][OPPOSITE[direction]] = False

    def _dfs_algo(self) -> None:
        """Carves passages using an iterative randomised DFS from (0, 0).

        Pre-marks "42" cells as visited on grids so DFS carves around them,
        leaving their walls intact.

        Raises:
            ValueError: If entry or exit overlaps a "42" stamp cell.
        """
        visited: List[List[bool]] = [
            [False] * self._width for _ in range(self._height)
        ]

        if self._height >= 9 and self._width >= 9:
            start_row = (self._height - 5) // 2
            start_col = (self._width - 7) // 2
            stamp: List[Tuple[int, int]] = [
                # 4
                (0, 0),
                (1, 0),
                (2, 0),
                (2, 1),
                (2, 2),
                (1, 2),
                (0, 2),
                (3, 2),
                (4, 2),
                # 2
                (0, 4),
                (0, 5),
                (0, 6),
                (1, 6),
                (2, 4),
                (2, 5),
                (2, 6),
                (3, 4),
                (4, 4),
                (4, 5),
                (4, 6),
            ]
            for r, c in stamp:
                if (c + start_col, r + start_row) == self._entry:
                    raise ValueError("ENTRY must not be on the 42_stamp")
                elif (c + start_col, r + start_row) == self._exit_pos:
                    raise ValueError("EXIT must not be on the 42_stamp")
                visited[r + start_row][c + start_col] = True
                self._stamp.append((r + start_row, c + start_col))

        stack: List[Tuple[int, int]] = [(0, 0)]
        visited[0][0] = True
        while stack:
            row, col = stack[-1]
            neigbors: List[Tuple[int, int, str]] = []
            for direcction in ["N", "E", "S", "W"]:
                dr, dc = MOVE[direcction]
                next_row = row + dr
                next_col = col + dc
                if (
                    0 <= next_row < self._height
                    and 0 <= next_col < self._width
                    and not visited[next_row][next_col]
                ):
                    neigbors.append((next_row, next_col, direcction))
            if neigbors:
                next_row, next_col, direcction = random.choice(neigbors)
                stack.append((next_row, next_col))
                visited[next_row][next_col] = True
                self._open_walls(row, col, direcction)
            else:
                stack.pop()

    def _is_valid_tobreak(self, row: int, col: int) -> bool:
        """Check if cell has fewer than 3 open walls.

        Args:
            row: cell row
            col: cell col

        Returns:
            True if safe to break, False otherwise
        """
        opened: int = 0
        for direction in ["N", "S", "E", "W"]:
            dr, dc = MOVE[direction]
            nr = row + dr
            nc = col + dc
            if not (0 <= nr < self._height and 0 <= nc < self._width):
                continue
            if not self._maze[row][col][direction]:
                opened += 1
        if opened < 3:
            return True
        return False

    def _break_more_walls(self) -> None:
        """Breaks ~15% of walls at random to introduce loops.

        Skips stamp cells, already-open walls, and cells that have already
        had a wall broken in this pass.
        """
        wallstobreak: int = int((self._width * self._height) * 0.15)
        breaked: int = 0
        visited: List[List[bool]] = [
            [False] * self._width for _ in range(self._height)
        ]
        while breaked < wallstobreak:
            row: int = random.randint(0, self._height - 1)
            col: int = random.randint(0, self._width - 1)
            direction: str = random.choice(["N", "E", "S", "W"])
            dr, dc = MOVE[direction]
            next_row = row + dr
            next_col = col + dc
            if not (
                0 <= next_row < self._height
                and 0 <= next_col < self._width
            ):
                continue
            if visited[row][col] or visited[next_row][next_col]:
                continue
            if (
                (row, col) in self._stamp
                or (next_row, next_col) in self._stamp
            ):
                continue
            if self._maze[row][col][direction] is False:
                continue
            if not self._is_valid_tobreak(row, col):
                continue
            if not self._is_valid_tobreak(next_row, next_col):
                continue
            self._open_walls(row, col, direction)
            visited[row][col] = True
            breaked += 1

    def _find_path(self) -> str:
        """Finds the shortest path from entry to exit using BFS.

        Returns:
            'N;E;S;W' direction string for the optimal route, e.g. 'SSEN'.
            Empty string if the exit is unreachable.
        """
        entryc: int = self._entry[0]
        entryr: int = self._entry[1]
        exitc: int = self._exit_pos[0]
        exitr: int = self._exit_pos[1]
        visited: List[List[bool]] = [
            [False] * self._width for _ in range(self._height)
        ]
        queue: deque[Tuple[int, int, str]] = deque()
        queue.append((entryr, entryc, ""))
        visited[entryr][entryc] = True
        while queue:
            row, col, path = queue.popleft()
            if row == exitr and col == exitc:
                return path
            for direction in ["N", "E", "S", "W"]:
                if not self._maze[row][col][direction]:
                    dr, dc = MOVE[direction]
                    next_row = row + dr
                    next_col = col + dc
                    if not visited[next_row][next_col]:
                        visited[next_row][next_col] = True
                        queue.append((next_row, next_col, path + direction))
        return ""
