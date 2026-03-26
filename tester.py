# maze = [
# [{'N': True, 'E': False, 'S': True, 'W': True}, {'N': True, 'E': False, 'S': True, 'W': False}, {'N': True, 'E': False, 'S': True, 'W': False}, {'N': True, 'E': True, 'S': False, 'W': False}, {'N': True, 'E': True, 'S': False, 'W': True}],
# [{'N': True, 'E': False, 'S': False, 'W': True}, {'N': True, 'E': False, 'S': True, 'W': False}, {'N': True, 'E': False, 'S': True, 'W': False}, {'N': False, 'E': False, 'S': True, 'W': False}, {'N': False, 'E': True, 'S': True, 'W': False}],
# [{'N': False, 'E': True, 'S': False, 'W': True}, {'N': True, 'E': False, 'S': False, 'W': True}, {'N': True, 'E': False, 'S': True, 'W': False}, {'N': True, 'E': False, 'S': True, 'W': False}, {'N': True, 'E': True, 'S': False, 'W': False}],
# [{'N': False, 'E': True, 'S': False, 'W': True}, {'N': False, 'E': True, 'S': False, 'W': True}, {'N': True, 'E': False, 'S': False, 'W': True}, {'N': True, 'E': True, 'S': False, 'W': False}, {'N': False, 'E': True, 'S': False, 'W': True}],
# [{'N': False, 'E': False, 'S': True, 'W': False}, {'N': False, 'E': True, 'S': True, 'W': False}, {'N': False, 'E': True, 'S': True, 'W': True}, {'N': False, 'E': False, 'S': True, 'W': True}, {'N': False, 'E': True, 'S': True, 'W': False}]]
# MOVE = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1)}
# def find_path() -> str:
#         """Find shortest path from entry to exit using BFS.
#         Returns:
#             Path string of N/E/S/W characters e.g. 'NNEESS'
#         """
#         from collections import deque
#         start_r: int = 0
#         start_c: int = 2
#         goal_r: int  = 4
#         goal_c: int  = 2
#         visited: list[list[bool]] = [[False] * 5 for _ in range(5)]
#         queue: deque[tuple[int, int, str]] = deque()
#         queue.append((start_r, start_c, ""))
#         visited[start_r][start_c] = True
#         while queue:
#             print(queue)
#             row, col, path = queue.popleft()
#             if row == goal_r and col == goal_c:
#                 return path

#             # check all 4 directions
#             for direction in ['N', 'E', 'S', 'W']:
#                 # wall must be OPEN
#                 if not maze[row][col][direction]:
#                     dr, dc = MOVE[direction]
#                     nr = row + dr
#                     nc = col + dc
#                     if not visited[nr][nc]:
#                         visited[nr][nc] = True
#                         queue.append((nr, nc, path + direction))
#         return ""
# import sys
# BOX = {
#     "NS":   "\u2551",
#     "EW":   "\u2550",
#     "NE":   "\u255a",
#     "NW":   "\u255d",
#     "SE":   "\u2554",
#     "SW":   "\u2557",
#     "NSE":  "\u2560",
#     "NSW":  "\u2563",
#     "NEW":  "\u2569",
#     "SEW":  "\u2566",
#     "NSEW": "\u256c",
#     "N":    "\u2568",
#     "S":    "\u2565",
#     "E":    "\u255e",
#     "W":    "\u2561",
#     "":     "\u00b7",
# }

# WALL   = "\u2588\u2588"
# CELL_W = 2

# YLW = '\033[93m'
# GRN = '\033[92m'
# RED = '\033[91m'
# RST = '\033[0m'
# def print_maze(
#     maze: list[list[dict[str, bool]]],
#     width: int,
#     height: int,
#     entry: tuple[int, int],
#     exit_pos: tuple[int, int],
#     path_cells: set[tuple[int, int]] | None = None,
#     solution: str = ""
# ) -> None:

#     rows: int = height * 2 + 1
#     cols: int = width  * 2 + 1

#     # True = solid wall
#     wall: list[list[bool]] = [[True] * cols for _ in range(rows)]

#     for row in range(height):
#         for col in range(width):
#             cell = maze[row][col]
#             cr, cc = row * 2 + 1, col * 2 + 1
#             wall[cr][cc] = False
#             if not cell['N']: wall[cr - 1][cc] = False
#             if not cell['S']: wall[cr + 1][cc] = False
#             if not cell['E']: wall[cr][cc + 1] = False
#             if not cell['W']: wall[cr][cc - 1] = False

#     # ── collect every grid slot that belongs to the solution path ─────────────
#     # We store ALL slots: cell interiors (odd,odd) AND connectors (even/odd mix)
#     path_slots: set[tuple[int, int]] = set()
#     if solution:
#         # cell interiors from path_cells param
#         if path_cells:
#             for (r, c) in path_cells:
#                 path_slots.add((r * 2 + 1, c * 2 + 1))

#         # walk the solution string and add both the connector slot AND the
#         # destination cell interior for every step
#         r, c = entry[1], entry[0]
#         path_slots.add((r * 2 + 1, c * 2 + 1))   # start cell
#         for direction in solution:
#             dr, dc = MOVE[direction]
#             connector_r = r * 2 + 1 + dr           # slot between cells
#             connector_c = c * 2 + 1 + dc
#             path_slots.add((connector_r, connector_c))
#             r += dr
#             c += dc
#             path_slots.add((r * 2 + 1, c * 2 + 1))  # destination cell

#     entry_gr = entry[1]    * 2 + 1
#     entry_gc = entry[0]    * 2 + 1
#     exit_gr  = exit_pos[1] * 2 + 1
#     exit_gc  = exit_pos[0] * 2 + 1

#     def box_char(r: int, c: int) -> str:
#         n = r > 0        and wall[r-1][c]
#         s = r < rows - 1 and wall[r+1][c]
#         e = c < cols - 1 and wall[r][c+1]
#         w = c > 0        and wall[r][c-1]
#         key = ("N" if n else "") + ("S" if s else "") +               ("E" if e else "") + ("W" if w else "")
#         vertical   = n or s
#         horizontal = e or w
#         if vertical and horizontal:
#             return BOX.get(key, "\u00b7")
#         elif horizontal:
#             return "\u2550"   # ═ plain horizontal
#         elif vertical:
#             return "\u2551"   # ║ plain vertical
#         else:
#             return "\u00b7"   # isolated

#     for gr in range(rows):
#         line = ""
#         for gc in range(cols):
#             even_r = (gr % 2 == 0)
#             even_c = (gc % 2 == 0)
#             on_path = (gr, gc) in path_slots
#             is_entry = (gr == entry_gr and gc == entry_gc)
#             is_exit  = (gr == exit_gr  and gc == exit_gc)

#             if wall[gr][gc]:
#                 # solid wall — never on path (path only goes through open slots)
#                 if even_r and even_c:
#                     line += box_char(gr, gc)
#                 elif even_r and not even_c:
#                     line += "\u2550" * CELL_W        # ══
#                 elif not even_r and even_c:
#                     line += "\u2551"                  # ║
#                 else:
#                     line += "\u2588" * CELL_W
#             else:
#                 # open slot — may be on path
#                 if is_entry:
#                     line += GRN + WALL + RST
#                     if even_r and not even_c:        # horizontal connector slot
#                         pass                          # WALL is already CELL_W wide
#                 elif is_exit:
#                     line += RED + WALL + RST
#                 elif on_path:
#                     # path color: fill the full visual width of this slot
#                     if even_r and even_c:            # open corner on path
#                         line += YLW + "\u2588" + RST
#                     elif even_r and not even_c:      # horizontal connector ══ → ██
#                         line += YLW + WALL + RST
#                     elif not even_r and even_c:      # vertical connector ║ → █
#                         line += YLW + "\u2588" + RST
#                     else:                            # cell interior
#                         line += YLW + WALL + RST
#                 else:
#                     # plain open space
#                     if even_r and even_c:
#                         line += " "
#                     elif even_r and not even_c:
#                         line += " " * CELL_W
#                     elif not even_r and even_c:
#                         line += " "
#                     else:
#                         line += " " * CELL_W

#         sys.stdout.write(line + "\n")
#         sys.stdout.flush()
# poth = find_path()
# print_maze(maze, 5, 5, (2, 0), (2, 4), solution=poth)
motion = "\033[5m"
path_color: str = "\033[11m"
path_color2: str = "\033[93m"
end_color: str = "\033[0m"
print(path_color2 + path_color +"""

                        ██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗                              
                        ██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝                              
                        ██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗                                
                        ██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝                                
                        ╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗                              
                         ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝                              
                                                                                                                    
                                                    ████████╗ ██████╗                                               
                                                    ╚══██╔══╝██╔═══██╗                                              
                                                       ██║   ██║   ██║                                              
                                                       ██║   ██║   ██║                                              
                                                       ██║   ╚██████╔╝                                              
                                                       ╚═╝    ╚═════╝                                               
                                                                                                                    
███╗   ███╗ █████╗ ███████╗███████╗     ██████╗ ███████╗███╗   ██╗███████╗██████╗  █████╗ ████████╗ ██████╗ ██████╗ 
████╗ ████║██╔══██╗╚══███╔╝██╔════╝    ██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
██╔████╔██║███████║  ███╔╝ █████╗      ██║  ███╗█████╗  ██╔██╗ ██║█████╗  ██████╔╝███████║   ██║   ██║   ██║██████╔╝
██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝      ██║   ██║██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██╗██╔══██║   ██║   ██║   ██║██╔══██╗
██║ ╚═╝ ██║██║  ██║███████╗███████╗    ╚██████╔╝███████╗██║ ╚████║███████╗██║  ██║██║  ██║   ██║   ╚██████╔╝██║  ██║
╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝🟥
                                                                                                                                            
""" + end_color)
