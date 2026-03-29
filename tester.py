import os
import sys
import termios
import tty
import time


def middel_print(message: str) -> None:
    RESET: str = '\033[0m'
    cols, _ = os.get_terminal_size()
    spaces: int = (cols - len(message)) // 2
    print((" " * spaces) +
          message + RESET)


def maze_controle() -> None:
    print("\n" * 3)
    middel_print("PRESS: " +
                 '\033[31m' + "(Q,q) to QUIT " + '\033[0m' +
                 "; (R,r) to regenerate ; (P,p) to Show PATH;")
    middel_print("(1) to change walls color     ;")
    middel_print("(2) to change path color      ;")
    middel_print("(3) to change walls Characters;")
    middel_print("(4) to change path Characters  ")
maze_controle()