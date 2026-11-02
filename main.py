from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from maze_generator import gen_maze, is_solvable
from maze_solver import ALGORITHMS, solve_maze

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Maze Lab")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend")), name="static")

@app.get("/")
def home(): return FileResponse(str(BASE_DIR / "frontend" / "index.html"))

@app.get("/maze/generate")
def generate_maze(rows: int = 31, cols: int = 31):
    if not (5 <= rows <= 101 and 5 <= cols <= 101):
        raise HTTPException(400, "Rows and columns must be between 5 and 101.")
    maze = gen_maze(rows, cols)
    if not is_solvable(maze): raise HTTPException(500, "The generated maze is not solvable.")
    return {"maze": maze, "rows": len(maze), "cols": len(maze[0])}

@app.post("/maze/solve")
def solve_current_maze(data: dict):
    maze, algorithm = data.get("maze"), data.get("algorithm", "linear")
    if algorithm not in ALGORITHMS or not isinstance(maze, list) or not maze or not isinstance(maze[0], list):
        raise HTTPException(400, "Invalid algorithm or maze.")
    cols = len(maze[0])
    if not (5 <= len(maze) <= 101 and 5 <= cols <= 101) or any(not isinstance(row, list) or len(row) != cols for row in maze) or any(type(cell) is not int or cell not in (0, 1) for row in maze for cell in row):
        raise HTTPException(400, "Maze dimensions or cell values are invalid.")
    solution, explored = solve_maze(maze, algorithm)
    return {"algorithm": algorithm, "solution": solution, "explored": explored, "path_length": len(solution) if solution else 0, "explored_count": len(explored), "message": "No solution found." if solution is None else ""}
