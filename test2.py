import random
import time
import sys
import os
import select
import termios
import tty

ROWS = 10
COLS = 10
DELAY_GEN = 0.02
DELAY_SOLVE = 0.03

WALL = "██"
EMPTY = "  "
PATH = "▓▓"
VISITED = "··"

RESET = "\033[0m"
HOME = "\033[H"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

WALL_COLOR = "\033[97m"
PATH_COLOR = "\033[92m"
VISITED_COLOR = "\033[96m"
START_COLOR = "\033[94m"
END_COLOR = "\033[91m"

SKIP_GEN = False
SKIP_SOLVE_SEARCH = False
SKIP_PATH_ANIM = False


def color(text: str, ansi: str) -> str:
    return f"{ansi}{text}{RESET}"


def make_odd(n: int) -> int:
    return n if n % 2 == 1 else n - 1


def get_key() -> str | None:
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1).lower()
    return None


def handle_keys() -> None:
    global SKIP_GEN, SKIP_SOLVE_SEARCH, SKIP_PATH_ANIM

    key = get_key()
    while key is not None:
        if key == "s":
            SKIP_GEN = True
            SKIP_SOLVE_SEARCH = True
            SKIP_PATH_ANIM = True
        elif key == "p":
            SKIP_SOLVE_SEARCH = True
        key = get_key()


def build_frame(
    maze: list[list[int]],
    start: tuple[int, int],
    end: tuple[int, int],
    current: tuple[int, int] | None = None,
    visited: set[tuple[int, int]] | None = None,
    final_path: set[tuple[int, int]] | None = None,
    title: str = "",
) -> str:
    if visited is None:
        visited = set()
    if final_path is None:
        final_path = set()

    lines = []
    lines.append(title)
    lines.append("")

    for r in range(len(maze)):
        row_parts = []
        for c in range(len(maze[0])):
            pos = (r, c)

            if pos == current:
                row_parts.append(color(PATH, PATH_COLOR))
            elif pos == start:
                row_parts.append(color(PATH, START_COLOR))
            elif pos == end:
                row_parts.append(color(PATH, END_COLOR))
            elif pos in final_path:
                row_parts.append(color(PATH, PATH_COLOR))
            elif pos in visited:
                row_parts.append(color(VISITED, VISITED_COLOR))
            elif maze[r][c] == 1:
                row_parts.append(color(WALL, WALL_COLOR))
            else:
                row_parts.append(EMPTY)
        lines.append("".join(row_parts))

    return "\n".join(lines)


def draw_frame(frame: str) -> None:
    sys.stdout.write(HOME)
    sys.stdout.write(frame)
    sys.stdout.flush()


def generate_maze_animated(rows: int, cols: int) -> list[list[int]]:
    rows = make_odd(rows)
    cols = make_odd(cols)

    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    start = (1, 1)
    end = (rows - 2, cols - 2)

    def carve(r: int, c: int) -> None:
        global SKIP_GEN

        maze[r][c] = 0

        handle_keys()
        if not SKIP_GEN:
            draw_frame(build_frame(
                maze, start, end,
                current=(r, c),
                title="Generating maze: breaking walls   [press s to skip]"
            ))
            time.sleep(DELAY_GEN)

        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        random.shuffle(directions)

        for dr, dc in directions:
            nr = r + dr
            nc = c + dc

            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and maze[nr][nc] == 1:
                maze[r + dr // 2][c + dc // 2] = 0

                handle_keys()
                if not SKIP_GEN:
                    draw_frame(build_frame(
                        maze, start, end,
                        current=(r + dr // 2, c + dc // 2),
                        title="Generating maze: breaking walls   [press s to skip]"
                    ))
                    time.sleep(DELAY_GEN)

                carve(nr, nc)

    carve(1, 1)
    maze[start[0]][start[1]] = 0
    maze[end[0]][end[1]] = 0

    draw_frame(build_frame(
        maze, start, end,
        title="Maze generated"
    ))

    return maze


def solve_maze_animated(
    maze: list[list[int]],
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    global SKIP_SOLVE_SEARCH, SKIP_PATH_ANIM

    stack = [start]
    parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    visited_set: set[tuple[int, int]] = set()

    while stack:
        r, c = stack.pop()

        if (r, c) in visited_set:
            continue

        visited_set.add((r, c))

        handle_keys()
        if not SKIP_SOLVE_SEARCH:
            draw_frame(build_frame(
                maze, start, end,
                current=(r, c),
                visited=visited_set,
                title="Solving maze: exploring cells   [press p to skip to path | s to show final]"
            ))
            time.sleep(DELAY_SOLVE)

        if (r, c) == end:
            break

        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr = r + dr
            nc = c + dc
            if 0 <= nr < len(maze) and 0 <= nc < len(maze[0]):
                if maze[nr][nc] == 0 and (nr, nc) not in parent:
                    parent[(nr, nc)] = (r, c)
                    stack.append((nr, nc))

    if end not in parent:
        return []

    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()

    if SKIP_PATH_ANIM:
        draw_frame(build_frame(
            maze, start, end,
            final_path=set(path),
            title="Solved maze: final path"
        ))
        return path

    final_path = set()
    for step in path:
        handle_keys()

        if SKIP_PATH_ANIM:
            draw_frame(build_frame(
                maze, start, end,
                final_path=set(path),
                title="Solved maze: final path"
            ))
            return path

        final_path.add(step)
        draw_frame(build_frame(
            maze, start, end,
            current=step,
            final_path=final_path,
            title="Solved maze: path goes cell to cell   [press s to show final]"
        ))
        time.sleep(DELAY_SOLVE)

    return path


def main() -> None:
    rows = ROWS
    cols = COLS
    start = (1, 1)
    end = (rows - 2, cols - 2)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)

        sys.stdout.write(HIDE_CURSOR)
        sys.stdout.write("\n" * (rows + 3))
        sys.stdout.flush()

        maze = generate_maze_animated(rows, cols)
        time.sleep(0.3)
        solve_maze_animated(maze, start, end)

        sys.stdout.write("\n")
        sys.stdout.flush()

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()


if __name__ == "__main__":
    os.system("clear")   # or "cls" on Windows
    main()