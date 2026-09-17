# mazegen

A dependency-free Python 3.10+ library for generating, validating, solving and
serializing rectangular mazes. Licensed under GPL-3.0-only; see the bundled
LICENSE.md in the distribution metadata.

## Install

```sh
python3 -m pip install ./mazegen-0.1.0-py3-none-any.whl
```

## Basic usage

```python
from mazegen import MazeGenerator, serialize_maze, write_output

generator = MazeGenerator(
    width=20, height=15,
    entry=(0, 0), exit=(19, 14),
    seed=42, perfect=False, algorithm="dfs",
)
maze = generator.generate()
solution = generator.shortest_path()
print(maze.walls)  # rows indexed as walls[y][x]
print(solution)  # (x, y) tuples, including entry and exit
print(generator.report)
text = serialize_maze(maze)
write_output(maze, "maze.txt")
```

## Parameters

- `width`, `height`: positive integers; at most 250,000 cells in total.
- `entry`, `exit`: distinct in-bounds `(x, y)` tuples.
- `seed`: integer, or `None` (default) for a randomly selected 64-bit seed.
- `perfect`: `False` by default; `True` generates a tree without loops.
- `algorithm`: `"dfs"` (default) or `"prim"`, case-insensitively.
- `include_pattern`: `True` by default; reserve fully closed cells spelling 42.

Non-perfect grids need at least two independent cycles. For example, a `2x2`
grid cannot satisfy this condition. Use a larger grid or `perfect=True`.
The same parameters and seed reproduce the same maze in the same runtime.

## Results and representation

- `generate()` returns a `Maze`, also available as `generator.maze`.
- `maze.walls[y][x]` is an integer wall mask: N=1, E=2, S=4, W=8.
- A set bit means a closed wall. `15` (`F`) means all four walls are closed.
- `maze.blocked` contains the fully closed decorative cells.
- `maze.open_neighbors((x, y))` yields connected traversable neighbours.
- `generator.shortest_path()` returns a shortest route including both endpoints.
- `generator.report` contains cell/edge counts, cycle rank, dead ends and length.
- `generator.operation_list` records permanent wall removals in order.
- `generator.diagnostics` explains why a 42 pattern could not be placed.

The library does not print diagnostics or launch a UI. Its caller decides how
to display messages. The main application's visualizer prints diagnostics.

## Errors

Catch `MazeError` for expected generation, validation and output failures:

```python
from mazegen import MazeError, MazeGenerator

try:
    generator = MazeGenerator(2, 2, (0, 0), (1, 1), perfect=False)
    generator.generate()
except MazeError as error:
    print(f"Cannot generate maze: {error}")
```

Call `generate()` before `shortest_path()`. Output parent directories must exist.
External borders and blocked cells must stay closed. A valid maze is connected
and has no fully open 3x3 area. Non-perfect mode also protects corners/centre.

## Rebuild from source

The repository provides `pyproject.toml`, the `mazegen/` sources and LICENSE.md.
With uv installed, run `uv build --wheel --out-dir .` at the repository root.
Poetry is not required. The wheel includes this guide and inline type hints.
