(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);

  const canvas = $("maze");
  const ctx = canvas.getContext("2d");
  const generateButton = $("generate-btn");
  const solveButton = $("solve-btn");
  const compareButton = $("compare-btn");
  const algorithmSelect = $("algorithm-select");
  const algorithmHelp = $("algorithm-help");
  const sizeInput = $("size-input");
  const sizeDisplay = $("size-display");
  const dimensionMeta = $("dimension-meta");
  const statusElement = $("status");
  const statusPill = statusElement.closest(".status");
  const results = $("results");
  const compareBody = document.querySelector("#compare-table tbody");
  const modeSwitch = document.querySelector(".mode-switch");
  const modeButtons = Array.from(document.querySelectorAll(".mode"));

  const MIN_SIZE = 5;
  const MAX_SIZE = 101;
  const DEFAULT_SIZE = 31;

  const modes = {
    classic: {
      label: "Classic Lab",
      help: "Uses the original neighbor-ordering strategies.",
      items: [
        ["sequential", "Sequential Search"],
        ["linear", "Linear Search"],
        ["bubble_sort", "Bubble Sort + Greedy"],
        ["insertion_sort", "Insertion Sort + Greedy"],
        ["selection_sort", "Selection Sort + Greedy"],
        ["quick_sort", "Quick Sort + Greedy"],
        ["shell_sort", "Shell Sort + Greedy"],
      ],
    },
    graph: {
      label: "Graph Lab",
      help: "Weighted grid graph algorithms with animated exploration.",
      items: [
        ["bfs", "Breadth-First Search"],
        ["dfs", "Depth-First Search"],
        ["dijkstra", "Dijkstra’s Algorithm"],
        ["a_star", "A* Search"],
        ["bellman_ford", "Bellman–Ford"],
      ],
    },
  };

  const css = getComputedStyle(document.documentElement);
  const token = (name, fallback) => css.getPropertyValue(name).trim() || fallback;
  const colors = {
    wall: token("--wall", "#1b2440"),
    path: token("--cell", "#ffffff"),
    explored: token("--explored", "#b8d7ff"),
    solution: token("--solution", "#ffb547"),
    start: token("--start", "#22a06b"),
    end: token("--end", "#e5486a"),
  };

  let mode = "classic";
  let maze = [];
  let cellSize = 10;
  let busy = false;

  /* ---------- UI helpers ---------- */

  function updateStatus(message, state = "idle") {
    statusElement.textContent = message;
    statusPill.dataset.state = state;
  }

  function updateDimensions(rows, cols) {
    sizeDisplay.textContent = cols;
    dimensionMeta.textContent = `${rows} × ${cols}`;
  }

  function setBusy(value) {
    busy = value;
    [generateButton, solveButton, compareButton, algorithmSelect, sizeInput, ...modeButtons].forEach((el) => {
      el.disabled = value;
    });
    canvas.setAttribute("aria-busy", String(value));
  }

  function escapeHtml(text) {
    return String(text).replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
  }

  function clampSize(value) {
    let size = parseInt(value, 10);
    if (!Number.isFinite(size)) size = DEFAULT_SIZE;
    return Math.min(MAX_SIZE, Math.max(MIN_SIZE, size));
  }

  /* ---------- Mode switching ---------- */

  function setMode(next, { focus = false } = {}) {
    if (busy || !modes[next]) return;
    mode = next;
    modeSwitch.dataset.active = mode;
    modeButtons.forEach((button) => {
      const active = button.dataset.mode === mode;
      button.classList.toggle("active", active);
      button.setAttribute("aria-selected", String(active));
      button.tabIndex = active ? 0 : -1;
      if (active && focus) button.focus();
    });
    algorithmSelect.innerHTML = modes[mode].items
      .map(([value, label]) => `<option value="${value}">${escapeHtml(label)}</option>`)
      .join("");
    algorithmHelp.textContent = modes[mode].help;
    results.hidden = true;
    updateStatus(`${modes[mode].label} ready`);
  }

  modeButtons.forEach((button, index) => {
    button.addEventListener("click", () => setMode(button.dataset.mode));
    button.addEventListener("keydown", (event) => {
      let target = null;
      if (event.key === "ArrowRight" || event.key === "ArrowDown") target = modeButtons[(index + 1) % modeButtons.length];
      else if (event.key === "ArrowLeft" || event.key === "ArrowUp") target = modeButtons[(index - 1 + modeButtons.length) % modeButtons.length];
      else if (event.key === "Home") target = modeButtons[0];
      else if (event.key === "End") target = modeButtons[modeButtons.length - 1];
      if (target) {
        event.preventDefault();
        setMode(target.dataset.mode, { focus: true });
      }
    });
  });

  /* ---------- API ---------- */

  async function request(url, options) {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  function solveRequest(algorithm) {
    return request("/maze/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ maze, algorithm }),
    });
  }

  /* ---------- Canvas ---------- */

  function fill(r, c, color) {
    ctx.fillStyle = color;
    ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
  }

  function drawEnds() {
    if (!maze.length) return;
    fill(0, 0, colors.start);
    fill(maze.length - 1, maze[0].length - 1, colors.end);
  }

  function draw() {
    if (!maze.length) return;
    const rows = maze.length;
    const cols = maze[0].length;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    cellSize = Math.max(2, Math.floor((960 * dpr) / Math.max(rows, cols)));
    canvas.width = cols * cellSize;
    canvas.height = rows * cellSize;
    canvas.style.aspectRatio = `${cols} / ${rows}`;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) fill(r, c, maze[r][c] ? colors.wall : colors.path);
    }
    drawEnds();
  }

  function paint(cells, color, frames) {
    return new Promise((resolve) => {
      if (!Array.isArray(cells) || !cells.length) {
        resolve();
        return;
      }
      const step = Math.max(1, Math.ceil(cells.length / frames));
      let i = 0;
      function tick() {
        for (const stop = Math.min(i + step, cells.length); i < stop; i++) fill(cells[i][0], cells[i][1], color);
        drawEnds();
        if (i < cells.length) requestAnimationFrame(tick);
        else resolve();
      }
      tick();
    });
  }

  /* ---------- Actions ---------- */

  async function generateMaze() {
    if (busy) return;
    setBusy(true);
    results.hidden = true;
    try {
      updateStatus("Generating a fresh maze…", "busy");
      const size = clampSize(sizeInput.value);
      const data = await request(`/maze/generate?rows=${size}&cols=${size}`);
      maze = data.maze;
      sizeInput.value = data.rows;
      updateDimensions(data.rows, data.cols);
      draw();
      updateStatus(`${data.rows} × ${data.cols} maze ready — choose an algorithm.`, "success");
    } catch (error) {
      updateStatus("Could not generate maze. Check the backend.", "error");
    } finally {
      setBusy(false);
    }
  }

  async function solveMaze() {
    if (busy) return;
    if (!maze.length) {
      updateStatus("Generate a maze first.", "error");
      return;
    }
    setBusy(true);
    try {
      const algorithm = algorithmSelect.value;
      const label = algorithmSelect.selectedOptions[0].text;
      draw();
      updateStatus(`${label}: exploring the maze…`, "busy");
      const data = await solveRequest(algorithm);
      await paint(data.explored, colors.explored, 90);
      if (!data.solution) {
        updateStatus(data.message || "No solution found.", "error");
        return;
      }
      updateStatus(`${label}: tracing the path…`, "busy");
      await paint(data.solution, colors.solution, 40);
      updateStatus(`${label}: ${data.path_length} cells in the path, ${data.explored_count} explored.`, "success");
    } catch (error) {
      updateStatus("Could not solve maze. Check the backend.", "error");
    } finally {
      setBusy(false);
    }
  }

  async function compareAll() {
    if (busy) return;
    if (!maze.length) {
      updateStatus("Generate a maze first.", "error");
      return;
    }
    setBusy(true);
    try {
      draw();
      const options = Array.from(algorithmSelect.options);
      const current = algorithmSelect.value;
      const out = [];
      for (const [index, option] of options.entries()) {
        updateStatus(`Benchmarking ${index + 1} of ${options.length}: ${option.textContent}…`, "busy");
        const data = await solveRequest(option.value);
        out.push({ value: option.value, name: option.textContent, path: data.path_length, explored: data.explored_count });
      }
      const valid = (n) => typeof n === "number" && Number.isFinite(n);
      const paths = out.map((x) => x.path).filter(valid);
      const explored = out.map((x) => x.explored).filter(valid);
      const minPath = paths.length ? Math.min(...paths) : null;
      const minExplored = explored.length ? Math.min(...explored) : null;
      const cell = (n, best) => `<td class="num${n === best ? " best" : ""}">${valid(n) ? n : "—"}</td>`;
      compareBody.innerHTML = out
        .map((x) => `<tr${x.value === current ? ' class="current"' : ""}><td>${escapeHtml(x.name)}</td>${cell(x.path, minPath)}${cell(x.explored, minExplored)}</tr>`)
        .join("");
      results.hidden = false;
      results.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "nearest" });
      updateStatus("Comparison complete — best values are highlighted.", "success");
    } catch (error) {
      updateStatus("Could not compare algorithms. Check the backend.", "error");
    } finally {
      setBusy(false);
    }
  }

  /* ---------- Wiring ---------- */

  generateButton.addEventListener("click", generateMaze);
  solveButton.addEventListener("click", solveMaze);
  compareButton.addEventListener("click", compareAll);
  sizeInput.addEventListener("input", () => {
    sizeDisplay.textContent = sizeInput.value || DEFAULT_SIZE;
  });
  sizeInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      generateMaze();
    }
  });
  sizeInput.addEventListener("blur", () => {
    if (!busy) {
      sizeInput.value = clampSize(sizeInput.value);
      sizeDisplay.textContent = sizeInput.value;
    }
  });

  setMode("classic");
  generateMaze();
})();