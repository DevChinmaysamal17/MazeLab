const canvas = document.getElementById("maze");
const ctx = canvas.getContext("2d");

const generateButton = document.getElementById("generate-btn");
const solveButton = document.getElementById("solve-btn");
const compareButton = document.getElementById("compare-btn");
const algorithmSelect = document.getElementById("algorithm-select");
const sizeInput = document.getElementById("size-input");

const MIN_SIZE = 5;
const MAX_SIZE = 101;
const statusElement = document.getElementById("status");
const compareTable = document.getElementById("compare-table");
const compareBody = compareTable.querySelector("tbody");

const COLORS = {
    wall: "#1f2937",
    path: "#ffffff",
    explored: "#bfdbfe",
    solution: "#f59e0b",
    start: "#16a34a",
    end: "#dc2626",
};

const CANVAS_PIXELS = 960;

let currentMaze = [];
let cellSize = 10;
let isBusy = false;


function setBusy(busy) {
    isBusy = busy;

    for (const control of [
        generateButton,
        solveButton,
        compareButton,
        algorithmSelect,
        sizeInput,
    ]) {
        control.disabled = busy;
    }
}


function updateStatus(message) {
    statusElement.textContent = message;
}


function algorithmLabel(value) {
    return algorithmSelect.querySelector(`option[value="${value}"]`).textContent;
}


async function request(url, options) {
    const response = await fetch(url, options);

    if (!response.ok) {
        throw new Error(`Request failed (${response.status})`);
    }

    return response.json();
}


function solveRequest(algorithm) {
    return request("/maze/solve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ maze: currentMaze, algorithm }),
    });
}


// Drawing

function fillCell(r, c, color) {
    ctx.fillStyle = color;
    ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
}


function drawEnds() {
    fillCell(0, 0, COLORS.start);
    fillCell(currentMaze.length - 1, currentMaze[0].length - 1, COLORS.end);
}


function drawMaze() {
    const rows = currentMaze.length;
    const cols = currentMaze[0].length;

    cellSize = Math.max(2, Math.floor(CANVAS_PIXELS / cols));
    canvas.width = cols * cellSize;
    canvas.height = rows * cellSize;

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            fillCell(r, c, currentMaze[r][c] === 1 ? COLORS.wall : COLORS.path);
        }
    }

    drawEnds();
}


// Paint cells a batch at a time so the search can be watched.
function paint(cells, color, frames) {
    return new Promise((resolve) => {
        const perFrame = Math.max(1, Math.ceil(cells.length / frames));
        let i = 0;

        function step() {
            const stop = Math.min(i + perFrame, cells.length);

            for (; i < stop; i++) {
                fillCell(cells[i][0], cells[i][1], color);
            }

            drawEnds();

            if (i < cells.length) {
                requestAnimationFrame(step);
            } else {
                resolve();
            }
        }

        step();
    });
}


// Actions

async function generateMaze() {
    if (isBusy) return;

    setBusy(true);
    compareTable.hidden = true;

    try {
        updateStatus("Generating maze...");

        // Clamp whatever was typed into the allowed range.
        let size = parseInt(sizeInput.value, 10);

        if (Number.isNaN(size)) size = 31;
        size = Math.min(MAX_SIZE, Math.max(MIN_SIZE, size));

        const data = await request(`/maze/generate?rows=${size}&cols=${size}`);

        currentMaze = data.maze;
        sizeInput.value = data.rows;
        drawMaze();

        updateStatus(
            `${data.rows} x ${data.cols} maze ready. Pick an algorithm and press Solve.`
        );

    } catch (error) {
        console.error(error);
        updateStatus("Could not generate maze. Check the backend.");

    } finally {
        setBusy(false);
    }
}


async function solveMaze() {
    if (isBusy) return;

    if (currentMaze.length === 0) {
        updateStatus("Generate a maze first.");
        return;
    }

    setBusy(true);

    try {
        const algorithm = algorithmSelect.value;

        drawMaze();
        updateStatus("Solving...");

        const data = await solveRequest(algorithm);

        await paint(data.explored, COLORS.explored, 90);

        if (!data.solution) {
            updateStatus(data.message || "No solution found.");
            return;
        }

        await paint(data.solution, COLORS.solution, 40);

        updateStatus(
            `${algorithmLabel(algorithm)}: path of ${data.path_length} cells, ` +
            `${data.explored_count} cells explored.`
        );

    } catch (error) {
        console.error(error);
        updateStatus("Could not solve maze. Check the backend.");

    } finally {
        setBusy(false);
    }
}


async function compareAll() {
    if (isBusy) return;

    if (currentMaze.length === 0) {
        updateStatus("Generate a maze first.");
        return;
    }

    setBusy(true);

    try {
        drawMaze();
        updateStatus("Running all algorithms...");

        const results = [];

        for (const option of algorithmSelect.options) {
            const data = await solveRequest(option.value);

            results.push({
                name: option.textContent,
                pathLength: data.path_length,
                explored: data.explored_count,
            });
        }

        const bestPath = Math.min(...results.map((r) => r.pathLength));
        const bestExplored = Math.min(...results.map((r) => r.explored));

        compareBody.innerHTML = "";

        for (const result of results) {
            const row = compareBody.insertRow();

            row.insertCell().textContent = result.name;

            const pathCell = row.insertCell();
            pathCell.textContent = result.pathLength;
            if (result.pathLength === bestPath) pathCell.classList.add("best");

            const exploredCell = row.insertCell();
            exploredCell.textContent = result.explored;
            if (result.explored === bestExplored) exploredCell.classList.add("best");
        }

        compareTable.hidden = false;
        updateStatus("Lowest values in each column are highlighted.");

    } catch (error) {
        console.error(error);
        updateStatus("Could not compare algorithms. Check the backend.");

    } finally {
        setBusy(false);
    }
}


generateButton.addEventListener("click", generateMaze);
solveButton.addEventListener("click", solveMaze);
compareButton.addEventListener("click", compareAll);
sizeInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") generateMaze();
});


// Generate the initial maze
generateMaze();