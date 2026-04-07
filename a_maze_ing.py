import select
import tty
import termios
import os
import time
import sys
from typing import List, Tuple
from classes import Config, DisplayConfig, MazeState
from parsing import parse_config


def grid_print(state: MazeState, config: Config) -> None:
    """Prints the maze grid centred in the terminal.

    Args:
        state: Current maze state holding the rendered grid.
        config: Config holding maze dimensions.
    """

    cols, rows = os.get_terminal_size()
    if cols < (config.width * 2 + 1) * 2 + 1 or rows < config.height * 2 + 12:
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


def print_maze(
        state: MazeState,
        config: Config,
        display: DisplayConfig
        ) -> None:
    """Builds and prints the full maze grid without the solution path.

    Args:
        state: Current maze state.
        config: Config holding maze dimensions and entry/exit positions.
        display: Display settings for wall color and character.
    """

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
    start_row = (config.height - 5) // 2
    start_col = (config.width - 7) // 2
    rows: int = config.height * 2 + 1
    cols: int = config.width * 2 + 1
    state.grid = [
        [display.wall_color + display.wall_char + "\033[0m"] * (cols)
        for _ in range(rows)
    ]
    for row in range(config.height):
        for col in range(config.width):
            cell = state.maze[row][col]
            cr: int = row * 2 + 1
            cc: int = col * 2 + 1
            state.grid[cr][cc] = "  "
            if cr == config.entry[1] * 2 + 1 and cc == config.entry[0] * 2 + 1:
                state.grid[cr][cc] = "\033[102m" + "EN" + "\033[0m"
            elif (
                cr == config.exit_pos[1] * 2 + 1
                and cc == config.exit_pos[0] * 2 + 1
            ):
                state.grid[cr][cc] = "\033[101m" + "EX" + "\033[0m"
            if not cell["N"]:
                state.grid[cr - 1][cc] = "  "
            if not cell["S"]:
                state.grid[cr + 1][cc] = "  "
            if not cell["E"]:
                state.grid[cr][cc + 1] = "  "
            if not cell["W"]:
                state.grid[cr][cc - 1] = "  "
    if config.height > 8 or config.width > 8:
        for r, c in stamp:
            state.grid[(r + start_row) * 2 + 1][(c + start_col) * 2 + 1] = (
                display.wall_color + display.wall_char + "\033[0m"
            )
    grid_print(state=state, config=config)
    maze_controle()


def print_path(
        state: MazeState,
        config: Config,
        display: DisplayConfig
        ) -> None:
    """Overwrite the solution path onto the grid and prints it.

    Args:
        state: Current maze state with a pre-built grid and solution string.
        config: Config holding entry position.
        display: Display settings for path color and character.
    """

    if state.solution:
        cr: int = config.entry[1] * 2 + 1
        cc: int = config.entry[0] * 2 + 1
        for move in state.solution:
            state.grid[cr][cc] = (
                display.path_color
                + display.path_char
                + "\033[0m"
            )
            if cr == config.entry[1] * 2 + 1 and cc == config.entry[0] * 2 + 1:
                state.grid[cr][cc] = "\033[102m" + "EN" + "\033[0m"
            if move == "N":
                state.grid[cr - 1][cc] = (
                    display.path_color + display.path_char + "\033[0m"
                )
                cr -= 2
            elif move == "S":
                state.grid[cr + 1][cc] = (
                    display.path_color + display.path_char + "\033[0m"
                )
                cr += 2
            elif move == "E":
                state.grid[cr][cc + 1] = (
                    display.path_color + display.path_char + "\033[0m"
                )
                cc += 2
            elif move == "W":
                state.grid[cr][cc - 1] = (
                    display.path_color + display.path_char + "\033[0m"
                )
                cc -= 2
            else:
                print("Error: Invalid path")
                exit(1)
    grid_print(state=state, config=config)
    maze_controle()


def welcom() -> None:
    """Prints the animated welcome screen,
    blocking until the terminal is large enough."""

    welcom_msg: List[str] = [
        " " * 24
        + "██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗██"
        + "█████╗",
        " " * 24
        + "██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██"
        + "╔════╝",
        " " * 24 + "██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║██" + "███╗",
        " " * 24 + "██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██" + "╔══╝",
        " " * 24
        + "╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║██"
        + "█████╗",
        " " * 24
        + " ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═"
        + "═════╝",
        "\n",
        " " * 48 + "████████╗ ██████╗",
        " " * 48 + "╚══██╔══╝██╔═══██╗",
        " " * 48 + "   ██║   ██║   ██║",
        " " * 48 + "   ██║   ██║   ██║",
        " " * 48 + "   ██║   ╚██████╔╝",
        " " * 48 + "   ╚═╝    ╚═════╝",
        "\n",
        "███╗   ███╗ █████╗ ███████╗███████╗     ██████╗ ███████╗███╗   ██╗"
        + "███████╗██████╗  █████╗ ████████╗ ██████╗ ██████╗",
        "████╗ ████║██╔══██╗╚══███╔╝██╔════╝    ██╔════╝ ██╔════╝████╗  ██║"
        + "██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗",
        "██╔████╔██║███████║  ███╔╝ █████╗      ██║  ███╗█████╗  ██╔██╗ ██║"
        + "█████╗  ██████╔╝███████║   ██║   ██║   ██║██████╔╝",
        "██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝      ██║   ██║██╔══╝  ██║╚██╗██║"
        + "██╔══╝  ██╔══██╗██╔══██║   ██║   ██║   ██║██╔══██╗",
        "██║ ╚═╝ ██║██║  ██║███████╗███████╗    ╚██████╔╝███████╗██║ ╚████║"
        + "███████╗██║  ██║██║  ██║   ██║   ╚██████╔╝██║  ██║",
        "╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝"
        + "╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝",
        " " * 106 + "\033[4m" "by mdahhou",
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
        print("\033[31m" + "\033[5m" + " " * spaces + msg + "\033[0m")
    print(
        "\033[92m"
        + "\033[5m"
        + ((" " * 46) + " " * spaces)
        + "Press 'S' to START!!"
        + "\033[0m"
    )


def exit_code() -> None:
    """Displays the goodbye animation and exits the program cleanly."""

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
            " " * 25 + "\033[4m" "by mdahhou",
        ]
        try:
            os.system("clear")
            cols, rows = os.get_terminal_size()
            spaces: int = (cols - 34) // 2
            print("\n" * rows)
            for msg in good_msg:
                print("\033[31m" + " " * spaces + msg + "\033[0m")
            for _ in range(rows):
                print()
                time.sleep(0.04)
            os.system("clear")
        except KeyboardInterrupt:
            os.system("clear")

    _good_bye()
    exit(0)


def middel_print(message: str) -> None:
    """Prints a message centred horizontally in the terminal.

    Args:
        message: The string to print centred.
    """

    cols, _ = os.get_terminal_size()
    spaces: int = (cols - len(message)) // 2
    print((" " * spaces) + message + "\033[0m")


def handel_exit(
    is_welcom: bool = False,
    state: MazeState | None = None,
    config: Config | None = None,
    display: DisplayConfig | None = None,
) -> None:
    """Prompts the user to confirm exit,
    returning to welcome or maze screen if declined.

    Args:
        is_welcom: If True, redraws the welcome screen on 'N'.
        Defaults to False.
        state: Current maze state, required if is_welcom is False.
        config: Current maze config, required if is_welcom is False.
        display: Current display settings, required if is_welcom is False.
    """

    middel_print(
        "Do u want really to "
        + "\033[31m" + "EXIT" + "\033[0m" + ": (Y)es, (N)o"
    )
    while True:
        char = get_char()
        if char in ["Y", "y"]:
            exit_code()
        elif char in ["N", "n"]:
            if is_welcom:
                welcom()
                break
            elif (
                state is not None
                and config is not None
                and display is not None
            ):
                redraw(state=state, config=config, display=display)
                break


def redraw(state: MazeState, config: Config, display: DisplayConfig) -> None:
    """Redraws either the maze or the path depending on current display state.

    Args:
        state: Current maze state.
        config: Config holding maze dimensions.
        display: Display settings including whether the path is visible.
    """

    if display.path:
        print_path(state=state, config=config, display=display)
    else:
        print_maze(state=state, config=config, display=display)


def maze_controle() -> None:
    """Prints the keybinding controls menu below the maze."""

    print("\n" * 3)
    msg: List[str] = [
        "PRESS: "
        + "\033[31m"
        + "(Q,q) to QUIT"
        + "\033[0m"
        + " ; (R,r) to REGENERATE ; (P,p) to Show PATH;",
        "(1) to change walls COLORS    ;",
        "(2) to change path COLORS     ;",
        "(3) to change walls CHARACTERS;",
        "(4) to change path CHARACTERS  ",
    ]
    for i in msg:
        middel_print(i)


def main() -> None:
    """Entry point — initialises state, runs the welcome loop, and handles all
    user input."""

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

    if len(sys.argv) != 2:
        print(
            "Error: The program must be run with the following command:\n"
            "python3 a_maze_ing.py [config_file_here]"
        )
        exit(1)
    while True:
        char: str = get_char()
        _check_terminal(True)
        if char in ["S", "s"]:
            os.system("clear")
            config = parse_config()
            state = MazeState(config=config)
            state.regenerate()
            print_maze(state=state, config=config, display=display)
            while True:
                char = get_char()
                _check_terminal()
                if char in ["R", "r"]:
                    config = parse_config()
                    state = MazeState(config=config)
                    state.regenerate()
                    print_maze(state=state, config=config, display=display)
                    display.path = False
                elif char in ["P", "p"]:
                    if not display.path:
                        print_path(state=state, config=config, display=display)
                        display.path = True
                    else:
                        print_maze(state=state, config=config, display=display)
                        display.path = False
                elif char == "1":
                    display.new_wall_color()
                    print_maze(state=state, config=config, display=display)
                    if display.path:
                        print_path(state=state, config=config, display=display)
                elif char == "2":
                    display.new_path_color()
                    if display.path:
                        print_path(state=state, config=config, display=display)
                elif char == "3":
                    display.new_wall_char()
                    print_maze(state=state, config=config, display=display)
                    if display.path:
                        print_path(state=state, config=config, display=display)
                elif char == "4":
                    display.new_path_char()
                    if display.path:
                        print_path(state=state, config=config, display=display)
                elif char in ["Q", "q"]:
                    handel_exit(
                        is_welcom=False,
                        state=state,
                        config=config,
                        display=display
                    )
        elif char in ["Q", "q"]:
            handel_exit(is_welcom=True)


def get_char() -> str:
    """Reads a single keypress from stdin without blocking.

    Returns:
        The character pressed, or an empty string if no input within timeout.
    """

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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        os.system("clear")
        middel_print("KeyboardInterrupt")
