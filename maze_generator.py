import random
from collections import deque

WALL = 1
PATH = 0


def gen_maze(rows=31, cols=31, loop_chance=0.08):
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
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == WALL and r % 2 != c % 2 and random.random() < loop_chance:
                maze[r][c] = PATH
    maze[-1][-1] = PATH
    return maze


def is_solvable(maze):
    if not maze or not maze[0] or maze[0][0] != PATH or maze[-1][-1] != PATH:
        return False
    rows, cols = len(maze), len(maze[0])
    if any(len(row) != cols for row in maze):
        return False
    queue, seen = deque([(0, 0)]), {(0, 0)}
    while queue:
        cell = queue.popleft()
        if cell == (rows - 1, cols - 1):
            return True
        for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            nxt = (cell[0] + dr, cell[1] + dc)
            if (0 <= nxt[0] < rows and 0 <= nxt[1] < cols and
                    maze[nxt[0]][nxt[1]] == PATH and nxt not in seen):
                seen.add(nxt)
                queue.append(nxt)
    return False
