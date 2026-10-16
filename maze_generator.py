import random
from collections import deque

WALL = 1
PATH = 0


def gen_maze(rows=31, cols=31, loop_chance=0.08):
    """Generate a maze with a recursive backtracker, then punch extra openings.

    Cells sit on even coordinates and the walls between them on odd ones, so
    both dimensions are rounded up to an odd number. The backtracker gives
    long winding corridors and many dead ends; the extra openings create loops,
    so there is more than one route from start to end.
    """

    if rows < 5 or cols < 5:
        raise ValueError("Rows and columns must be at least 5.")

    rows += rows % 2 == 0
    cols += cols % 2 == 0

    maze = [[WALL] * cols for _ in range(rows)]

    maze[0][0] = PATH
    stack = [(0, 0)]

    while stack:
        r, c = stack[-1]

        options = []
        for dr, dc in ((0, 2), (2, 0), (0, -2), (-2, 0)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == WALL:
                options.append((nr, nc, dr, dc))

        if not options:
            stack.pop()
            continue

        nr, nc, dr, dc = random.choice(options)
        maze[r + dr // 2][c + dc // 2] = PATH
        maze[nr][nc] = PATH
        stack.append((nr, nc))

    # Open some walls that separate two cells (exactly one odd coordinate).
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == WALL and r % 2 != c % 2:
                if random.random() < loop_chance:
                    maze[r][c] = PATH

    return maze


def is_solvable(maze):
    """Check whether the destination is reachable from the start."""

    if not maze or not maze[0]:
        return False

    rows = len(maze)
    cols = len(maze[0])

    if any(len(row) != cols for row in maze):
        return False

    if maze[0][0] != PATH or maze[rows - 1][cols - 1] != PATH:
        return False

    queue = deque([(0, 0)])
    visited = {(0, 0)}

    while queue:
        r, c = queue.popleft()

        if (r, c) == (rows - 1, cols - 1):
            return True

        for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            nr, nc = r + dr, c + dc

            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and maze[nr][nc] == PATH
                and (nr, nc) not in visited
            ):
                visited.add((nr, nc))
                queue.append((nr, nc))

    return False