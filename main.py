from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from maze_generator import gen_maze, is_solvable
from maze_solver import ALGORITHMS, solve_maze


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

MIN_SIZE = 5
MAX_SIZE = 101

app = FastAPI(title="Maze Lab")

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static",
)


@app.get("/")
def home():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/maze/generate")
def generate_maze(rows: int = 31, cols: int = 31):
    if not (MIN_SIZE <= rows <= MAX_SIZE and MIN_SIZE <= cols <= MAX_SIZE):
        raise HTTPException(
            status_code=400,
            detail=f"Rows and columns must be between {MIN_SIZE} and {MAX_SIZE}.",
        )

    maze = gen_maze(rows, cols)

    if not is_solvable(maze):
        raise HTTPException(
            status_code=500,
            detail="The generated maze is not solvable.",
        )

    # gen_maze rounds even sizes up to odd, so report the real dimensions.
    return {
        "maze": maze,
        "rows": len(maze),
        "cols": len(maze[0]),
    }


@app.post("/maze/solve")
def solve_current_maze(data: dict):
    maze = data.get("maze")
    algorithm = data.get("algorithm", "linear")

    if algorithm not in ALGORITHMS:
        raise HTTPException(status_code=400, detail="Invalid algorithm.")

    if (
        not isinstance(maze, list)
        or not maze
        or not isinstance(maze[0], list)
        or not maze[0]
    ):
        raise HTTPException(status_code=400, detail="Invalid maze.")

    rows = len(maze)
    cols = len(maze[0])

    if (
        not (MIN_SIZE <= rows <= MAX_SIZE and MIN_SIZE <= cols <= MAX_SIZE)
        or any(not isinstance(row, list) or len(row) != cols for row in maze)
        or any(
            type(cell) is not int or cell not in (0, 1)
            for row in maze
            for cell in row
        )
    ):
        raise HTTPException(
            status_code=400,
            detail="Maze dimensions or cell values are invalid.",
        )

    solution, explored = solve_maze(maze, algorithm)

    if solution is None:
        return {
            "algorithm": algorithm,
            "solution": None,
            "explored": explored,
            "message": "No solution found.",
        }

    return {
        "algorithm": algorithm,
        "solution": solution,
        "explored": explored,
        "path_length": len(solution),
        "explored_count": len(explored),
    }