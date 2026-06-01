*This project has been created as part of the 42 curriculum by [carltruj], [jovillal].*

# A-Maze-ing: Advanced Procedural Generation, Topological Solving & Monolithic Package Distribution

---

## 📖 1. System Overview & Core Philosophy

**A-Maze-ing** is a high-performance Python 3.10+ implementation designed to model, carve, topologic-validate, and serialize perfect mazes. The execution lifecycle decouples pure mathematical grid generation from the interactive rendering and deployment layers. 

The software operates as a deterministic finite state machine where a configuration schema is parsed, converted into a bit-masked multi-dimensional array, mapped into a single Spanning Tree graph, solved via uniform-cost pathfinders, and exported into low-level hexadecimal strings. Every subroutine adheres strictly to `PEP 8` via `flake8` and is fully typed to pass `mypy --strict`.

---

## ⚙️ 2. Configuration Schema & Structural Parsing

The system reads parameters via a strict flat-file `KEY=VALUE` parser. The input stream tokenizes lines, stripping whitespace and filtering comments.

### Configuration Specification Matrix

* **WIDTH / HEIGHT (`int`)**: Discrete grid boundaries ($X$ and $Y$ dimensions). Must be $>1$.
* **ENTRY / EXIT (`Tuple[int, int]`)**: Sub-indexed spatial coordinates mapping the starting vertex and terminal target. Validated to ensure `ENTRY` $\neq$ `EXIT` and that both reside inside the bounding box.
* **OUTPUT_FILE (`str`)**: Character string identifying the target file descriptor for hexadecimal stream serialization.
* **PERFECT (`bool`)**: Master toggle enforcing the single-path topological tree rule.

---

## 🧠 3. Deep Dive: Internal Algorithmic Architecture

To understand how the program manages memory states and graph traversals without overhead or stack corruption, the engine splits its execution into three low-level core layers:

### A. Matrix Layout & Bitwise Representation
Instead of using complex object-oriented overhead for cell objects, the grid is stored as a lightweight 2D matrix of raw integers (`List[List[int]]`). Each cell uses 4 bits to store its state, where a bit value of `1` means the wall is closed, and `0` means it is open:
* `Bit 0 (value 1)`: North Direction
* `Bit 1 (value 2)`: East Direction
* `Bit 2 (value 4)`: South Direction
* `Bit 3 (value 8)`: West Direction

An unvisited cell starts completely sealed, represented by the integer `15` ($1 + 2 + 4 + 8$, or binary `1111`). Opening a pathway uses bitwise AND along with a bitwise NOT mask. For example, clearing an East wall uses:
$$\text{cell\_value} = \text{cell\_value} \ \& \ \sim\text{EAST}$$

### B. The Carving Engine: Iterative Randomized DFS
The engine generates the maze layout using an optimized **Randomized Depth-First Search (DFS)**, implemented with an explicit loop-stack to prevent the recursion limits inherent to Python's interpreter.

1. **Initialization:** Every cell is set to `15`. If dimensions allow, the program centers the "42" shape, marking those cells as immutable walls and automatically adjusting their neighbors to keep the layout synchronized.
2. **The Loop Lifecycle:** The carver starts at the parsed `ENTRY` cell, flags it as visited, and pushes it onto the execution stack.
3. **Neighbor Evaluation:** The engine queries adjacent cells using directional offset vectors. If unvisited neighbors are found, one is selected at random using a pseudo-random seed generator.
4. **The Look-Ahead Guard:** Before breaking a wall, the carver runs `would_create_3x3_open_space()`. It simulates the removal; if the resulting move creates an open room cluster where 4 or more adjacent celdas are fully hollowed out, the transition is aborted, enforcing a clean, narrow corridor layout.
5. **Carving & Traversal:** If the path is valid, the current cell's directional bit and the neighbor's opposite bit are flipped to `0`. The neighbor is pushed onto the stack, and the loop advances. If a dead end is hit, the stack pops backward to find the last available junction.

### C. The Solving Engine: Queue-Based BFS Pathfinding
Once the maze is generated, the pathfinder maps the shortest route from `ENTRY` to `EXIT` using a **Breadth-First Search (BFS)** tracking queue.

1. **Queue Tracking:** The queue initializes with an array containing the starting coordinate path: `[[self.entry]]`.
2. **Exploration Paths:** The loop dequeues the oldest tracking sequence. It reads the current coordinates and extracts its bitmask value.
3. **Valid Transitions:** The solver runs bitwise checks on the current cell value against directional masks: `if not (current_cell_value & DIRECTION)`. If the bit is `0`, the pathway is clear.
4. **Cycle Mitigation:** If the neighboring cell is unvisited, it is saved into a historical lookup `Set`. The new coordinates are appended to the path sequence and queued back for evaluation.
5. **Termination:** Because the DFS carver guarantees a perfect maze (a Spanning Tree structure), the first path that reaches the `EXIT` coordinates is mathematically guaranteed to be the single, shortest solution path. The matching moves are immediately converted into a clean string sequence of cardinal directions (`N`, `E`, `S`, `W`).

---

## 💾 4. Low-Level Hexadecimal Serialization

The output system exports data row-by-row, translating the integer bitmasks into uppercase hexadecimal tokens. A double newline (`\n\n`) separates the structural matrix from the metadata footer, ensuring full compatibility with automated grading scripts.

### Hex Output Blueprint
```text
9C6C6C6C6C6A   <-- Row 0 Hex Strings (\n)
C40000000003   <-- Row 1 Hex Strings (\n)
514444444421   <-- Row 2 Hex Strings (\n)
               <-- Double Newline Divider
0,0            <-- Transposed ENTRY Coordinates (X,Y\n)
19,14          <-- Transposed EXIT Coordinates (X,Y\n)
EESSEENWWNNE   <-- Shortest Path Directions String (\n)