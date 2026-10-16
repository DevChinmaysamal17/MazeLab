ALGORITHMS = (
    "linear",
    "greedy",
    "selection_sort",
    "insertion_sort",
    "bubble_sort",
    "shell_sort",
    "quick_sort",
)

# Fixed scan order: up, left, down, right.
DIRECTIONS = [
    (-1, 0),
    (0, -1),
    (1, 0),
    (0, 1),
]


def get_neighbors(maze, visited, row, col):
    # Return walkable, unvisited neighboring cells.
    rows = len(maze)
    cols = len(maze[0])
    neighbors = []
    for dr, dc in DIRECTIONS:
        nr = row + dr
        nc = col + dc
        if (
            0 <= nr < rows
            and 0 <= nc < cols
            and maze[nr][nc] == 0
            and not visited[nr][nc]
        ):
            neighbors.append((nr, nc))
    return neighbors


def distance(cell, end):
    # Calculate Manhattan distance to the destination.
    return abs(cell[0] - end[0]) + abs(cell[1] - end[1])


def sequential_search(neighbors):
    # Return the first available neighbor.
    if neighbors:
        return neighbors[0]
    return None


def greedy_search(neighbors, end):
    # Choose the neighbor closest to the destination.
    if not neighbors:
        return None
    best = neighbors[0]
    for cell in neighbors[1:]:
        if distance(cell, end) < distance(best, end):
            best = cell
    return best


def selection_sort(neighbors, end):
    # Sort neighbors by distance using Selection Sort.
    cells = neighbors.copy()
    n = len(cells)
    for i in range(n):
        min_index = i
        for j in range(i + 1, n):
            if distance(cells[j], end) < distance(cells[min_index], end):
                min_index = j
        cells[i], cells[min_index] = cells[min_index], cells[i]
    return cells


def insertion_sort(neighbors, end):
    # Sort neighbors by distance using Insertion Sort.
    cells = neighbors.copy()
    for i in range(1, len(cells)):
        current = cells[i]
        j = i - 1
        while j >= 0 and distance(cells[j], end) > distance(current, end):
            cells[j + 1] = cells[j]
            j -= 1
        cells[j + 1] = current
    return cells


def bubble_sort(neighbors, end):
    # Sort neighbors by distance using Bubble Sort.
    cells = neighbors.copy()
    n = len(cells)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if distance(cells[j], end) > distance(cells[j + 1], end):
                cells[j], cells[j + 1] = cells[j + 1], cells[j]
                swapped = True
        if not swapped:
            break
    return cells


def shell_sort(neighbors, end):
    # Sort neighbors by distance using Shell Sort.
    cells = neighbors.copy()
    n = len(cells)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            current = cells[i]
            current_distance = distance(current, end)
            j = i
            while j >= gap and distance(cells[j - gap], end) > current_distance:
                cells[j] = cells[j - gap]
                j -= gap
            cells[j] = current
        gap //= 2
    return cells


def quick_sort(neighbors, end):
    # Sort neighbors by distance using Quick Sort.
    cells = neighbors.copy()

    def partition(low, high):
        pivot_distance = distance(cells[high], end)
        i = low - 1
        for j in range(low, high):
            if distance(cells[j], end) <= pivot_distance:
                i += 1
                cells[i], cells[j] = cells[j], cells[i]
        cells[i + 1], cells[high] = cells[high], cells[i + 1]
        return i + 1

    def quick_sort_recursive(low, high):
        if low < high:
            pivot_index = partition(low, high)
            quick_sort_recursive(low, pivot_index - 1)
            quick_sort_recursive(pivot_index + 1, high)

    quick_sort_recursive(0, len(cells) - 1)
    return cells


def order_neighbors(neighbors, algorithm, end):
    # Order neighboring cells using the selected strategy.
    if algorithm == "linear":
        return neighbors.copy()
    if algorithm == "greedy":
        best = greedy_search(neighbors, end)
        if best is None:
            return []
        return [best] + [cell for cell in neighbors if cell != best]
    if algorithm == "selection_sort":
        return selection_sort(neighbors, end)
    if algorithm == "insertion_sort":
        return insertion_sort(neighbors, end)
    if algorithm == "bubble_sort":
        return bubble_sort(neighbors, end)
    if algorithm == "shell_sort":
        return shell_sort(neighbors, end)
    if algorithm == "quick_sort":
        return quick_sort(neighbors, end)
    raise ValueError("Unknown algorithm")


def solve_maze(maze, algorithm="linear"):
    # Solve the maze using the selected strategy and backtracking.

    # Returns (path, explored). The path is None if no solution exists.
    
    if algorithm not in ALGORITHMS:
        raise ValueError("Unknown algorithm")
    if not maze or not maze[0]:
        return None, []
    rows = len(maze)
    cols = len(maze[0])
    if any(len(row) != cols for row in maze):
        return None, []
    start = (0, 0)
    end = (rows - 1, cols - 1)
    if maze[0][0] != 0 or maze[rows - 1][cols - 1] != 0:
        return None, []
    visited = [[False] * cols for _ in range(rows)]
    visited[0][0] = True
    # Each stack entry stores a cell and its remaining candidate moves.
    stack = [(start, None)]
    path = [start]
    explored = [start]
    while stack:
        current, candidates = stack[-1]
        row, col = current
        if current == end:
            return (
                [[r, c] for r, c in path],
                [[r, c] for r, c in explored],
            )
        if candidates is None:
            neighbors = get_neighbors(maze, visited, row, col)
            candidates = order_neighbors(neighbors, algorithm, end)
            stack[-1] = (current, candidates)
        if candidates:
            next_cell = candidates.pop(0)
            nr, nc = next_cell
            if not visited[nr][nc]:
                visited[nr][nc] = True
                path.append(next_cell)
                explored.append(next_cell)
                stack.append((next_cell, None))
        else:
            stack.pop()
            path.pop()
    return None, [[r, c] for r, c in explored]
