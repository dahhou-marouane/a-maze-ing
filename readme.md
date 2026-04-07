*This project has been created as part of the 42 curriculum by mdahhou, njabbar*

---

# A-Maze-ing 🌀

## Description

A-Maze-ing is a terminal-based maze generator and visualizer written in Python. Given a configuration file, it generates a randomized maze, displays it in the terminal with full color and character customization, and writes the result to an output file in a hexadecimal wall-encoding format.

Key features:
- Perfect or imperfect maze generation (with or without loops)
- Reproducible mazes via an optional seed
- BFS shortest-path solver with visual overlay
- Interactive terminal controls (colors, characters, regeneration, path toggle, exit)
- A **"42" pixel-art** embedded in every maze large enough to contain it
- Reusable `MazeGenerator` class packaged as a standalone pip-installable module

---

## Instructions

### Requirements

- Python 3.10 or later
- Dependencies listed in `requirements.txt`

### Installation

```bash
make install
```

### Run

```bash
make run
# which runs:
python3 a_maze_ing.py config.txt
```

### Other Makefile targets

```bash
make lint      # run flake8 and mypy
make debug     # run with pdb debugger
make clean     # remove __pycache__, .mypy_cache, etc.
```

---

## Configuration File Format

The config file uses one `KEY=VALUE` pair per line. Lines starting with `#` are treated as comments and ignored.

| Key           | Description                              | Example                   |
|---------------|------------------------------------------|---------------------------|
| `WIDTH`       | Number of columns in the maze            | `WIDTH=20`                |
| `HEIGHT`      | Number of rows in the maze               | `HEIGHT=20`               |
| `ENTRY`       | Entry cell coordinates `(x,y)`           | `ENTRY=0,0`               |
| `EXIT`        | Exit cell coordinates `(x,y)`            | `EXIT=19,19`              |
| `OUTPUT_FILE` | Output filename (must be in script dir)  | `OUTPUT_FILE=maze.txt`    |
| `PREFECT`     | Perfect maze? (`True`/`False`)           | `PREFECT=True`            |
| `SEED`        | Optional RNG seed for reproducibility    | `SEED=42`                 |

**Example `config.txt`:**

```ini
# A-Maze-ing configuration
WIDTH=20
HEIGHT=20
ENTRY=0,0
EXIT=19,19
OUTPUT_FILE=maze.txt
PREFECT=True
SEED=42
```

---

## Output File Format

Each cell is encoded as a single hexadecimal digit representing its closed walls:

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1       | East  |
| 2       | South |
| 3       | West  |

A wall being closed sets its bit to `1`; open means `0`.

After the grid (one row per line), a blank line separates three additional lines:
1. Entry coordinates `x,y`
2. Exit coordinates `x,y`
3. Shortest path as a string of `N`, `E`, `S`, `W` characters

---

## Maze Generation Algorithm

This project uses **Iterative Depth-First Search (DFS)** with a randomised neighbour selection — also known as the *recursive backtracker*.

**Why DFS?**
- Natively generates perfect mazes (one path between any two cells) as a spanning tree
- Simple and efficient to implement iteratively using a stack

For imperfect mazes (`PREFECT=False`), approximately 15% of additional walls are broken at random after DFS, introducing loops and multiple routes.

---

## Reusable Module — `mazegen`

The maze generation logic is fully encapsulated in the `MazeGenerator` class inside `mazegen.py`, which is also packaged as a pip-installable module (`mazegen-*.whl`) at the root of this repository.

### Installation from package

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic usage

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=20, height=20, entry=(0, 0), exit=(19, 19))
gen.generate()

maze = gen.maze()      # List[List[Dict[str, bool]]] — the grid
path = gen.solution()  # str — e.g. 'SSEENNE...'
```

### Custom parameters

```python
gen = MazeGenerator(
    width=30,
    height=30,
    entry=(0, 0),
    exit=(29, 29),
    prefect=False,   # allow loops
    seed="hello42"   # reproducible output
)
gen.generate()
```

### Accessing the structure

`gen.maze()` returns a 2D list where each cell is a dict:

```python
cell = maze[row][col]
# cell = {'N': True, 'E': False, 'S': True, 'W': False}
# True  = wall is present (closed)
# False = wall is removed (open passage)
```

`gen.solution()` returns a string of `N`/`E`/`S`/`W` characters representing the BFS shortest path from entry to exit.

### Building the package from source

```bash
pip install build
python3 -m build
# Outputs to dist/
```

---

## Interactive Controls

Once the maze is displayed, the following keys are available:

| Key     | Action                          |
|---------|---------------------------------|
| `R / r` | Regenerate a new maze           |
| `P / p` | Toggle shortest path display    |
| `1`     | Cycle wall colors               |
| `2`     | Cycle path colors               |
| `3`     | Cycle wall characters           |
| `4`     | Cycle path characters           |
| `Q / q` | Quit                            |

---

## Resources

### References
- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Python `termios` documentation](https://docs.python.org/3/library/termios.html)
- [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [Python packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

### AI Usage
Claude was used throughout this project to assist with:
- Writing and reviewing PEP 257-compliant Google-style docstrings
- Debugging terminal rendering issues (resize detection, raw mode input)
- Explaining low-level concepts (`termios`, `select`, ANSI codes, `nonlocal`)
- Reviewing config parsing and error handling logic
- Styling this readme file

All AI-generated content was reviewed, tested, and fully understood before inclusion.

---

## Team & Project Management

### Team Members

| Member   | Role                                                                                                      |
|----------|-----------------------------------------------------------------------------------------------------------|
| mdahhou  | Maze generation algorithm, DFS/BFS logic, output format, visual rendering, interactive controls, etc.     |
| njabbar  | Configuration file parsing, input validation, and error handling                                          |

### Planning

**Initial plan:** Split work cleanly between generation (mdahhou) and display (njabbar), integrate at the end.

**How it evolved:** Integration revealed coupling issues early — the original `AllData` god-object was refactored into `Config`, `DisplayConfig`, and `MazeState` to make functions independently testable and clearer to reason about. This added time but improved overall code quality significantly.

### What Worked Well
- DFS algorithm was straightforward to implement and produced great-looking mazes
- Separating the `MazeGenerator` into its own module made packaging trivial
- The `42` stamp approach (pre-marking cells before DFS) was elegant

### What Could Be Improved
- Terminal resize detection could be handled with `signal.SIGWINCH` instead of polling
- The imperfect wall-breaking strategy could be smarter (avoid creating 3×3 open areas)
- A second algorithm (e.g. Prim's) would be a nice bonus

### Tools Used
- `mypy` for static type checking
- `flake8` for style linting
- Claude for AI assistance
- Git with feature branches for collaboration