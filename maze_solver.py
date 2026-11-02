from collections import deque
import heapq

CLASSIC_ALGORITHMS = ("sequential", "linear", "bubble_sort", "insertion_sort", "selection_sort", "quick_sort", "shell_sort")
GRAPH_ALGORITHMS = ("bfs", "dfs", "dijkstra", "a_star", "bellman_ford")
ALGORITHMS = CLASSIC_ALGORITHMS + GRAPH_ALGORITHMS
DIRECTIONS = [(-1, 0), (0, -1), (1, 0), (0, 1)]


def neighbors(maze, cell):
    r, c = cell
    for dr, dc in DIRECTIONS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and maze[nr][nc] == 0:
            yield (nr, nc)


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def sort_neighbors(items, algorithm, end):
    values = list(items)
    if algorithm in ("sequential", "linear"):
        return values
    if algorithm == "bubble_sort":
        for i in range(len(values)):
            for j in range(len(values) - i - 1):
                if distance(values[j], end) > distance(values[j + 1], end):
                    values[j], values[j + 1] = values[j + 1], values[j]
    elif algorithm == "insertion_sort":
        for i in range(1, len(values)):
            item, j = values[i], i - 1
            while j >= 0 and distance(values[j], end) > distance(item, end):
                values[j + 1] = values[j]
                j -= 1
            values[j + 1] = item
    elif algorithm == "selection_sort":
        for i in range(len(values)):
            best = min(range(i, len(values)), key=lambda n: distance(values[n], end))
            values[i], values[best] = values[best], values[i]
    else:
        values.sort(key=lambda item: distance(item, end))
    return values


def rebuild(parent, end):
    path, current = [], end
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()
    return [[r, c] for r, c in path]


def solve_classic(maze, algorithm):
    start, end = (0, 0), (len(maze) - 1, len(maze[0]) - 1)
    seen, parent, explored = {start}, {start: None}, [start]
    stack = [(start, None)]
    while stack:
        current, candidates = stack[-1]
        if current == end:
            return rebuild(parent, end), [[r, c] for r, c in explored]
        if candidates is None:
            candidates = sort_neighbors((n for n in neighbors(maze, current) if n not in seen), algorithm, end)
            stack[-1] = (current, candidates)
        if candidates:
            nxt = candidates.pop(0)
            if nxt not in seen:
                seen.add(nxt); parent[nxt] = current; explored.append(nxt); stack.append((nxt, None))
        else:
            stack.pop()
    return None, [[r, c] for r, c in explored]


def solve_graph(maze, algorithm):
    # Unit edge weights make BFS equivalent to Bellman–Ford here while
    # preserving the algorithm's path/exploration contract for the UI.
    if algorithm == "bellman_ford":
        return solve_graph(maze, "bfs")
    start, end = (0, 0), (len(maze) - 1, len(maze[0]) - 1)
    parent, explored, seen, closed = {start: None}, [], {start}, set()
    queue = deque([start])
    distances = {start: 0}
    heap = [(0, start)] if algorithm in ("a_star", "dijkstra") else []
    if algorithm == "dfs":
        queue = [start]
    while queue or heap:
        if algorithm == "bfs": current = queue.popleft()
        elif algorithm == "dfs": current = queue.pop()
        elif algorithm in ("a_star", "dijkstra"):
            _, current = heapq.heappop(heap)
            if current in closed: continue
            closed.add(current)
        else:
            current = queue.popleft() if queue else None
        if current is None: break
        explored.append(current)
        if current == end: return rebuild(parent, end), [[r, c] for r, c in explored]
        for nxt in neighbors(maze, current):
            new_cost = distances[current] + 1
            if algorithm == "bellman_ford" or nxt not in distances or new_cost < distances[nxt]:
                distances[nxt] = new_cost; parent[nxt] = current
                if nxt not in seen:
                    seen.add(nxt)
                    if algorithm == "dfs": queue.append(nxt)
                    elif algorithm in ("a_star", "dijkstra"): heapq.heappush(heap, (new_cost + (distance(nxt, end) if algorithm == "a_star" else 0), nxt))
                    else: queue.append(nxt)
    return None, [[r, c] for r, c in explored]


def solve_maze(maze, algorithm="linear"):
    if algorithm not in ALGORITHMS or not maze or not maze[0] or maze[0][0] or maze[-1][-1]:
        return None, []
    return solve_graph(maze, algorithm) if algorithm in GRAPH_ALGORITHMS else solve_classic(maze, algorithm)
