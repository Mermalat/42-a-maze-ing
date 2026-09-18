*This project has been created as part of the 42 curriculum by alpturan, memalli.*

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator, validator, solver, serializer, reusable
package, and interactive terminal visualizer.

The application reads a `KEY=VALUE` configuration file, creates either a
perfect maze or a loop-rich Pac-Man-style board, writes the result using the
required hexadecimal wall encoding, calculates a shortest solution, and then
opens an interactive terminal interface.

The project also contains a reusable `mazegen` package. Maze generation,
validation, solving, and output encoding do not depend on the terminal user
interface, so they can be imported by another Python project.

## Table of contents

- [Project goals](#project-goals)
- [Description](#description)
- [Instructions](#instructions)
- [Main features](#main-features)
- [Requirements](#requirements)
- [Project structure](#project-structure)
- [Installation](#installation)
- [Running the application](#running-the-application)
- [Configuration file](#configuration-file)
- [Execution flow](#execution-flow)
- [Maze representation](#maze-representation)
- [Wall encoding](#wall-encoding)
- [Generation algorithms](#generation-algorithms)
- [The 42 pattern](#the-42-pattern)
- [Perfect mode](#perfect-mode)
- [Non-perfect mode](#non-perfect-mode)
- [Structural validation](#structural-validation)
- [Shortest-path solver](#shortest-path-solver)
- [Output file format](#output-file-format)
- [Terminal visualizer](#terminal-visualizer)
- [Animation model](#animation-model)
- [Reusable package](#reusable-package)
- [Error handling](#error-handling)
- [Makefile targets](#makefile-targets)
- [Testing strategy](#testing-strategy)
- [Performance and limits](#performance-and-limits)
- [Team and project management](#team-and-project-management)
- [AI usage](#ai-usage)
- [Troubleshooting](#troubleshooting)
- [Evaluation checklist](#evaluation-checklist)
- [Resources](#resources)
- [License](#license)

## Project goals

The main goal is to produce structurally valid rectangular mazes while keeping
the generation code independent from display and command-line concerns.

The program is designed around the following responsibilities:

1. Parse and validate user configuration.
2. Create a coherent grid whose cells contain four wall bits.
3. Reserve fully closed cells that visibly form the number `42`.
4. Generate a spanning tree with DFS or randomized Prim.
5. Optionally add safe extra passages for non-perfect mode.
6. Validate wall symmetry, borders, connectivity, cycles, and open areas.
7. Find a shortest route from entry to exit.
8. Serialize the maze in the subject-required text format.
9. Display and animate the maze in the terminal.
10. Expose the generator through an importable Python package.

## Main features

- Python 3.10 or later.
- Required one-argument command-line interface.
- Strict `KEY=VALUE` configuration parsing.
- Reproducible generation with an optional integer seed.
- Randomized depth-first search generation.
- Randomized Prim generation.
- Perfect maze mode with no graph cycles.
- Non-perfect mode with at least two independent cycles.
- Full connectivity for all traversable cells.
- Coherent walls between every pair of neighbouring cells.
- Permanently closed outer borders.
- Prevention of fully open `3x3` areas.
- A visible `42` made from fully closed cells when dimensions allow it.
- Breadth-first shortest-path solving.
- Hexadecimal wall serialization.
- Interactive path visibility.
- Runtime wall-colour rotation.
- Regeneration without restarting the program.
- Animated replay of permanent wall removals.
- Runtime switching between DFS and Prim.
- Runtime switching between perfect and non-perfect modes.
- Static checking with flake8 and mypy.
- Build metadata for a reusable `mazegen-*` distribution.

## Requirements

The project expects:

- Python 3.10 or later.
- `uv` for dependency management and package builds.
- A terminal that supports ANSI escape sequences for colours.
- Linux or macOS for the terminal application (`termios` is used).

The standalone `mazegen` library has no terminal dependency. Poetry is not
needed for development, installation, or package builds.

The application itself has no third-party runtime dependency. Development
dependencies are declared in `pyproject.toml`:

- `flake8` for style checking.
- `mypy` for static type checking.

## Project structure

The important source files are organized as follows:

```text
.
├── a_maze_ing.py
├── config.txt
├── LICENSE.md
├── Makefile
├── mazegen-0.1.0-py3-none-any.whl
├── pyproject.toml
├── README.md
├── uv.lock
├── mazegen/
│   ├── config_parser.py
│   ├── __init__.py
│   ├── errors.py
│   ├── generator.py
│   ├── model.py
│   ├── output.py
│   ├── README.md
│   ├── py.typed
│   ├── solver.py
│   └── validation.py
└── visualizer/
    ├── __init__.py
    └── visualizer.py
```

File responsibilities:

- `a_maze_ing.py` is the required command-line entry point.
- `config_parser.py` reads and validates configuration values.
- `mazegen/model.py` defines directions, wall bits, maze data, and operations.
- `mazegen/generator.py` implements DFS, Prim, braiding, and `42` placement.
- `mazegen/validation.py` checks structural invariants and graph statistics.
- `mazegen/solver.py` implements shortest-path search and direction encoding.
- `mazegen/output.py` serializes and writes the required output format.
- `visualizer/visualizer.py` renders, animates, and controls the maze.
- `mazegen/README.md` is the usage guide included in the reusable wheel.
- `pyproject.toml` contains package and build configuration.
- `LICENSE.md` defines the reuse and redistribution terms.

## Instructions

Python 3.10+ runs the application directly. Install uv for the development
commands below; see <https://docs.astral.sh/uv/getting-started/installation/>.

### Installation

Install the development environment with:

```sh
make install
```

The target runs `uv sync --locked`, creates `.venv` and installs the versions
recorded in `uv.lock`. Python requirements are enforced by uv.

The equivalent direct commands are:

```sh
uv sync --locked
```

## Running the application

The exact command required by the subject is:

```sh
python3 a_maze_ing.py config.txt
```

The program accepts exactly one positional argument. The filename can differ,
but it must point to a valid configuration file:

```sh
python3 a_maze_ing.py examples/large_maze.txt
```

Create this example file first; only `config.txt` is supplied by default.

The Makefile wrapper uses `config.txt` by default:

```sh
make run
```

Another configuration can be selected through the Make variable:

```sh
make run CONFIG=my_config.txt
```

If zero arguments or more than one argument are passed, the program prints:

```text
Usage: python3 a_maze_ing.py config.txt
```

## Configuration file

The configuration format contains one `KEY=VALUE` pair per line.

Blank lines are ignored. A line whose first non-whitespace character is `#`
is treated as a comment.

Spaces around keys and values are removed by the parser.

### Mandatory keys

| Key | Meaning | Example |
| --- | --- | --- |
| `WIDTH` | Number of cells on the x-axis | `WIDTH=20` |
| `HEIGHT` | Number of cells on the y-axis | `HEIGHT=15` |
| `ENTRY` | Entry coordinate in `x,y` form | `ENTRY=0,0` |
| `EXIT` | Exit coordinate in `x,y` form | `EXIT=19,14` |
| `OUTPUT_FILE` | Destination of the encoded maze | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Select perfect or non-perfect mode | `PERFECT=False` |

### Optional keys

| Key | Meaning | Default |
| --- | --- | --- |
| `SEED` | Integer random seed | A random 64-bit value |
| `ALGORITHM` | `DFS` or `PRIM` | `DFS` |
| `DELAY` | Animation delay in seconds | `0.02` |

### Complete example

```ini
# Reproducible non-perfect maze
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
ALGORITHM=DFS
DELAY=0.02
```

### Coordinate convention

Coordinates always use `(x, y)` order:

- `x` increases from left to right.
- `y` increases from top to bottom.
- `(0, 0)` is the top-left cell.
- `(WIDTH - 1, HEIGHT - 1)` is the bottom-right cell.

The entry and exit must both be inside the grid and must be different.

### Boolean convention

`PERFECT` accepts `True` or `False` without case sensitivity. Values such as
`yes`, `1`, or `enabled` are rejected.

The supplied configuration uses `PERFECT=False`, as does the reusable
generator's default. The `PERFECT` key remains mandatory in configuration files.

### Seed behaviour

When `SEED` is present, creating a maze with the same dimensions, mode,
algorithm, entry, exit, and seed produces the same structure.

When `SEED` is absent, `MazeGenerator` obtains a random 64-bit value from the
`secrets` module. The chosen value is stored on the generated `Maze` object.

### Delay behaviour

`DELAY` must be a finite, non-negative number. It represents the initial wait
between animation operations.

A delay of `0` selects maximum animation speed.

Every regeneration resets the live delay to the configured initial value.

## Execution flow

The normal program flow is:

```text
config file
    |
    v
parse_config()
    |
    v
MazeGenerator(...)
    |
    v
generate()
    |
    +--> choose safe 42 pattern
    +--> initialize every wall as closed
    +--> carve a DFS or Prim spanning tree
    +--> braid the maze when PERFECT=False
    +--> validate all structural invariants
    |
    v
write_output()
    |
    v
MazeVisualizer.run()
```

`a_maze_ing.py` catches expected `ConfigError` and `MazeError` exceptions,
prints a readable `Error: ...` message to standard error, and exits with a
non-zero status.

Ctrl-C during generation exits with status 130. During visualization it exits
cleanly after the terminal input settings are restored. Recoverable menu
generation errors keep the previous maze and mode available.

## Maze representation

The `Maze` dataclass stores:

- `width` and `height`.
- `entry` and `exit` coordinates.
- The effective random `seed`.
- The `perfect` mode flag.
- A two-dimensional list of wall integers.
- A frozen set of blocked `42` cells.

Rows are stored in `walls[y][x]` order.

All cells begin with the integer `15`, written as hexadecimal `F`. This means
that North, East, South, and West are all closed.

`Maze.remove_wall()` always updates both cells sharing a wall. Opening the East
wall of one cell also opens the West wall of its neighbour.

`Maze.add_wall()` performs the opposite coherent update.

`remove_wall()` rejects external borders and blocked decorative cells.
`add_wall()` only closes shared walls and rejects external shared-wall requests.

### Geometric and open neighbours

Two different neighbour concepts are deliberately used:

- `MazeGenerator._grid_neighbors()` returns geometrically adjacent cells that
  are inside the grid and are not blocked. It does not require a passage to be
  open. Generation needs this function because every wall begins closed.
- `Maze.open_neighbors()` returns only neighbours connected by an already open
  passage. Solving, degree counting, connectivity checking, and validation use
  this function.

Confusing these operations would prevent the first wall from being carved or
would allow the solver to walk through closed walls.

## Wall encoding

Each cell uses the lower four bits of an integer:

| Bit | Value | Direction | Meaning when set |
| --- | ---: | --- | --- |
| 0 | `1` | North | North wall is closed |
| 1 | `2` | East | East wall is closed |
| 2 | `4` | South | South wall is closed |
| 3 | `8` | West | West wall is closed |

Examples:

- `0` (`0000`) has no closed walls.
- `1` (`0001`) has only its North wall closed.
- `3` (`0011`) has North and East closed.
- `A` (`1010`) has East and West closed.
- `F` (`1111`) is fully closed.

The serializer emits uppercase hexadecimal digits.

Wall values outside the inclusive range `0..15` are rejected by validation.

## Generation algorithms

Both supported algorithms first create a spanning tree over every traversable
cell. A spanning tree connects all vertices with exactly `V - 1` edges and has
no cycle.

The same `random.Random(seed)` instance controls every randomized choice.

DFS was chosen for its simple stack-based implementation and long corridors.
Prim provides a contrasting branching pattern through the same wall API.

### Randomized DFS

DFS is implemented as an iterative recursive-backtracker.

The algorithm:

1. Selects a random traversable start cell.
2. Adds that cell to a reached set and an explicit stack.
3. Looks for unreached geometric neighbours of the stack's top cell.
4. Randomly selects one available neighbour.
5. Removes the shared wall and records the operation.
6. Pushes the new cell onto the stack.
7. Pops when the current cell has no unreached neighbour.
8. Continues until the stack is empty.

DFS commonly creates long winding corridors and deep branches.

An explicit stack is used instead of Python recursion, avoiding recursion-depth
failures on large mazes.

### Randomized Prim

Prim generation grows one connected region through a frontier list.

The algorithm:

1. Selects a random traversable start cell.
2. Adds all geometric edges leaving that cell to the frontier.
3. Randomly removes one frontier edge.
4. Ignores it if its destination has already been reached.
5. Otherwise opens the edge and reaches the new cell.
6. Adds the new cell's unreached neighbour edges to the frontier.
7. Continues until the frontier is empty.

Randomized Prim usually creates shorter branches and a visibly different
topology from DFS.

### Why both algorithms use one interface

`MazeGenerator._carve_tree()` selects the configured algorithm but both
implementations produce the same outputs:

- A connected tree.
- Coherent wall removals.
- An ordered `operation_list`.
- A structure compatible with the common braiding phase.
- A structure compatible with the same validator and solver.

This separation made it possible to add Prim without changing output encoding
or terminal rendering.

## The 42 pattern

The visible `42` is defined as a seven-column, five-row mask:

```text
X.X.XXX
X.X...X
XXX.XXX
..X.X..
..X.XXX
```

Every `X` becomes a blocked cell whose wall value remains `F`.

The generator searches for a placement close to the centre and requires a
one-cell margin around the pattern. It therefore needs at least a `9x7` grid
for the standard placement search.

A candidate placement is rejected when it:

- Covers the entry.
- Covers the exit.
- Covers one of the four corners.
- Covers the selected centre cell.
- Disconnects the remaining traversable grid.
- Prevents non-perfect mode from supporting two independent cycles.

If no safe placement exists, generation continues without the pattern and adds
a diagnostic message explaining why it was omitted.

Blocked cells are excluded from generation, solving, connectivity checks, and
dead-end statistics.

## Perfect mode

Perfect mode is selected with:

```ini
PERFECT=True
```

In this mode, the DFS or Prim spanning tree is kept without adding extra
passages.

For the traversable graph:

```text
open_edges = traversable_cells - 1
cycle_rank = 0
```

Because the graph is connected and has no cycle, exactly one path exists
between any two traversable cells, including entry and exit.

The fully closed decorative cells are not part of the traversable graph.

## Non-perfect mode

Non-perfect mode is selected with:

```ini
PERFECT=False
```

The generator first creates the same spanning tree and then calls `_braid()`.

Braiding performs up to three dead-end reduction passes:

1. Collect cells whose open degree is exactly one.
2. Shuffle them using the seeded random generator.
3. Find their closed walls leading to traversable neighbours.
4. Prefer candidate neighbours with lower degree.
5. Open the first wall that does not create a forbidden open `3x3` area.

After dead-end reduction, additional closed edges are considered until the
target number of added cycles is reached where possible.

The target is based on:

```text
max(2, traversable_cell_count // 12)
```

Validation always requires at least two independent cycles. A perfect maze or
a maze with only one extra loop is rejected in this mode.

The following cells must remain traversable and reachable:

- Top-left corner.
- Top-right corner.
- Bottom-left corner.
- Bottom-right corner.
- Centre cell `(width // 2, height // 2)`.

The validator allows at most two real dead ends in non-perfect mode. A corridor
whose other sides all face the 42 pattern or the outer border is counted as an
enclosed dead end, matching the subject analyzer's exception. The report keeps
both the total `dead_ends` and the actionable `real_dead_ends` counts.

## Structural validation

Every generated maze passes through `validate_maze()` before it is returned or
serialized.

Validation checks:

1. The number of wall rows equals `height`.
2. Every row contains exactly `width` cells.
3. Entry and exit differ.
4. Entry and exit are inside the grid.
5. Entry and exit are not blocked.
6. Every wall value is between `0` and `F`.
7. Shared walls are symmetrical.
8. Every external border remains closed.
9. Every decorative cell is fully closed.
10. At least two traversable cells exist.
11. Every traversable cell belongs to one connected component.
12. No traversable cell is isolated.
13. No fully open `3x3` window exists.
14. Perfect mode has cycle rank zero.
15. Non-perfect mode keeps corners and centre open.
16. Non-perfect mode has at least two independent cycles.
17. Entry can reach exit through open passages.
18. Non-perfect mode has at most two real dead ends.

### Cycle rank

For one connected undirected graph, cycle rank is calculated as:

```text
cycle_rank = open_edges - traversable_cells + 1
```

Interpretation:

- `0` means a tree with no loop.
- `1` means one independent loop.
- `2` or more means several independent route choices.

### Open-area protection

Before the braider permanently removes a wall, it temporarily opens that wall
and checks every affected `3x3` window.

A window is forbidden only when all twelve internal connections of its nine
cells are open. Windows containing blocked `42` cells are not treated as open
areas.

If the candidate wall creates a forbidden area, the wall is restored. A final
full-grid scan is also performed during validation.

### Validation report

Successful validation returns a `ValidationReport` containing:

- `traversable_cells`.
- `open_edges`.
- `cycle_rank`.
- `dead_ends`.
- `real_dead_ends` (excludes geometrically unavoidable enclosed cells).
- `solution_length`.

The last report is available as `generator.report`.

## Shortest-path solver

The solver uses breadth-first search because every maze passage has equal
cost.

The search maintains:

- A queue of cells waiting to be explored.
- A `previous` dictionary used to reconstruct the route.
- Only neighbours returned by `Maze.open_neighbors()`.

When the destination is reached, the solver walks backwards through the
`previous` mapping and reverses the result.

The returned coordinate list includes both entry and exit.

For example:

```python
[(0, 0), (1, 0), (1, 1), (2, 1)]
```

`path_to_directions()` converts coordinate differences to letters:

- `(0, -1)` becomes `N`.
- `(1, 0)` becomes `E`.
- `(0, 1)` becomes `S`.
- `(-1, 0)` becomes `W`.

Non-adjacent path elements are rejected.

## Output file format

The output begins with one hexadecimal character per cell and one grid row per
line.

After the grid there is:

1. One empty line.
2. Entry coordinates.
3. Exit coordinates.
4. The shortest path as `N`, `E`, `S`, and `W` letters.

Minimal valid perfect maze output for a `2x2` grid:

```text
D3
D6

0,0
1,1
ES
```

Here entry moves East, then South to reach exit. This tiny maze cannot contain
the 42 pattern and must use `PERFECT=True`, as it cannot hold two loops.

Every line, including the final path line, ends with `\n`.

Before serialization, the maze is validated again. A supplied custom solution
must:

- Start at the maze entry.
- End at the maze exit.
- Use only open adjacent passages.
- Have the same length as a canonical shortest path.

The output writer converts permission and operating-system errors into
`MazeOutputError` with a readable filename-specific message.

## Terminal visualizer

The terminal renderer clearly distinguishes:

- Maze walls.
- Entry, displayed as `E`.
- Exit, displayed as `X`.
- Shortest-path cells, displayed with a coloured dot.
- Blocked `42` cells, displayed as solid blocks.

The interactive menu provides:

| Option | Action |
| ---: | --- |
| `1` | Generate a new random maze |
| `2` | Show or hide the shortest path |
| `3` | Rotate wall colours |
| `4` | Switch between DFS and Prim |
| `5` | Switch between perfect and non-perfect mode |
| `6` | Quit |

### Regeneration

Option `1` replaces the current seed with a new random 64-bit value, generates
a new maze, writes it to the configured output path, clears the path overlay,
and replays the animation.

### Path toggle

The shortest path is calculated lazily the first time option `2` is selected.
Later selections reuse the stored path and change only its visibility.

### Colour rotation

Option `3` rotates between the built-in ANSI TrueColor wall palettes.

Entry, exit, path, and pattern colours are separate from the wall palette.

### Algorithm toggle

Option `4` changes `dfs` to `prim` or `prim` to `dfs`. It keeps the same seed,
allowing the two algorithms to be compared under the same random input value.

### Mode toggle

Option `5` changes the perfect flag and regenerates with the same seed. This
makes the effect of the common braiding phase easier to observe.

### Terminal interruption

`EOF` at the menu and `Ctrl-C` during animation or menu operations leave the
visualizer cleanly. The terminal's original settings are restored in a finally
block. Invalid mode changes report an error and retain the previous maze.

## Animation model

Every permanent passage opening is stored as a `CellOperation` containing:

- `source` coordinate.
- `target` coordinate.
- `operation`, currently `REMOVE_WALL`.

Animation creates a temporary maze where every cell begins fully closed. It
then applies `generator.operation_list` in generation order.

The final maze is not reconstructed by guessing from the output file. It is
replayed from the same coherent mutations used during generation.

During animation:

- Left arrow increases delay and slows the animation.
- Right arrow decreases delay and speeds the animation.
- Delay never becomes negative.
- The left-arrow adjustment caps the delay at one second.
- Current operation number and speed are displayed.

When standard input is not a TTY, live key reading is skipped safely.
When standard output is not a TTY, animated frames are skipped and the final
maze is rendered directly. This keeps redirected and automated runs fast.

## Reusable package

The reusable public API is exported by `mazegen/__init__.py`.

The primary class is `MazeGenerator`:

```python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    seed=42,
    perfect=False,
    algorithm="prim",
)

maze = generator.generate()
solution = generator.shortest_path()

print(maze.to_hex_lines())
print(solution)
print(generator.report)
```

### Constructor parameters

| Parameter | Type | Purpose |
| --- | --- | --- |
| `width` | `int` | Grid width |
| `height` | `int` | Grid height |
| `entry` | `tuple[int, int]` | Start coordinate |
| `exit` | `tuple[int, int]` | Destination coordinate |
| `seed` | `int \| None` | Reproducible randomness |
| `perfect` | `bool` | Select graph mode |
| `include_pattern` | `bool` | Enable safe `42` placement |
| `algorithm` | `str` | Select `dfs` or `prim` |

### Accessible results

After `generate()`:

- `generator.maze` references the generated `Maze`.
- `generator.report` references its `ValidationReport`.
- `generator.operation_list` contains replayable wall openings.
- `generator.diagnostics` contains nonfatal generation notes.
- `generator.shortest_path()` returns a shortest coordinate route.

### Standalone helper functions

The public package also exports:

- `shortest_path()`.
- `path_to_directions()`.
- `serialize_maze()`.
- `write_output()`.
- `validate_maze()`.
- `has_open_3x3()`.

### Building the distribution

Build package artifacts with:

```sh
uv build
```

For the subject requirement that the installable file be located at the
repository root, build with an explicit output directory:

```sh
uv build --out-dir .
```

The distribution name is `mazegen`. `make build` creates only
`mazegen-0.1.0-py3-none-any.whl` at repository root, as required for submission.
The `uv_build` backend is used; Poetry and poetry-core are not dependencies.
The wheel includes the Python modules, `mazegen/README.md`, the type marker
`py.typed`, and the license. The full application is run from the repository.

Test the produced wheel or source archive in a fresh virtual environment before
submission.

For example, starting at repository root:

```sh
python3 -m venv /tmp/mazegen-wheel-check
/tmp/mazegen-wheel-check/bin/python -m pip install ./mazegen-0.1.0-py3-none-any.whl
cd /tmp
/tmp/mazegen-wheel-check/bin/python -c "from mazegen import MazeGenerator; print(MazeGenerator(20, 15, (0, 0), (19, 14), seed=42).generate().to_hex_lines())"
```

Run outside the repository so the source folder cannot mask a broken installed
package. Use a new temporary directory if the example environment already exists.
To rebuild during evaluation, install uv, run `make install`, `make lint`, then
`make build` in a fresh checkout containing all the source and build inputs.

## Error handling

Expected failures use project-specific exceptions:

- `ConfigError` for missing or malformed configuration.
- `MazeGenerationError` for impossible generation parameters.
- `MazeValidationError` for structural inconsistencies.
- `MazeOutputError` for invalid serialization or file writing.
- `MazeError` as the common base for maze-related failures.

Configuration errors include:

- File not found.
- Permission denied.
- Invalid UTF-8.
- Missing `=`.
- Empty key or value.
- Duplicate key.
- Missing mandatory key.
- Invalid integer.
- Non-positive dimensions.
- Invalid coordinate syntax.
- Out-of-bounds entry or exit.
- Equal entry and exit.
- Invalid `PERFECT` value.
- Invalid algorithm name.
- Negative, infinite, or non-numeric delay.

Generation errors include:

- More than 250,000 cells.
- Fewer than two total cells.
- Invalid coordinate object.
- Invalid seed type.
- Invalid mode type.
- Unsupported algorithm.
- Dimensions that cannot support two cycles in non-perfect mode.
- Failure to connect every traversable cell.

## Makefile targets

The Makefile currently defines:

| Target | Purpose |
| --- | --- |
| `install` | Synchronize dependencies and check Python version |
| `run` | Run `a_maze_ing.py` with `CONFIG` |
| `debug` | Start the required script under Python pdb |
| `build` | Build the reusable wheel in repository root |
| `clean` | Remove Python and tool caches plus build directories |
| `lint` | Run project flake8 and configured mypy checks |
| `lint-strict` | Run flake8 and mypy strict mode |
| `fclean` | Also remove the local `.venv` after cleaning |

Examples:

```sh
make install
make run
make run CONFIG=config.txt
make debug
make build
make lint
make lint-strict
make clean
```

At the pdb prompt, use `n` to step, `c` to continue and `q` to quit.
`clean` preserves the required root-level wheel and configuration files.

## Testing strategy

Generation should be tested across a matrix rather than with one visually
pleasing output.

Recommended dimensions include:

- Very small valid perfect mazes.
- Small mazes that cannot contain the `42` pattern.
- Thin mazes.
- Square mazes.
- Rectangular mazes.
- The default `20x15` maze.
- Larger mazes below the 250,000-cell limit.

Recommended parameter combinations include:

- DFS with `PERFECT=True`.
- DFS with `PERFECT=False`.
- Prim with `PERFECT=True`.
- Prim with `PERFECT=False`.
- Fixed seeds.
- Automatically generated seeds.
- Entry and exit in corners.
- Entry and exit away from corners.

Important assertions include:

- Same inputs and seed produce the same maze.
- Shared walls agree in both directions.
- External borders are closed.
- Every traversable cell is reachable.
- Entry reaches exit.
- No traversable cell is isolated.
- No forbidden open `3x3` exists.
- Perfect mode has cycle rank zero.
- Non-perfect mode has cycle rank at least two.
- Required non-perfect key cells are traversable.
- Output has exactly one hex digit per cell.
- Output ends with a newline.
- The encoded solution uses only `N`, `E`, `S`, and `W`.
- Replaying the solution ends at the configured exit.

### Static checks

Run:

```sh
make lint
```

For stronger local checks, run:

```sh
make lint-strict
```

### Analyzer checks

The subject's optional `maze_analyzer.py` can be obtained from the assignment
resources; it is not a runtime or build dependency. Place it locally before
running the following commands.

After generating a maze, inspect it with:

```sh
python3 maze_analyzer.py maze.txt
```

Do not rely only on the analyzer process exit code. Read the reported fields:

- Reachable region.
- Unreachable corridors.
- Independent loops.
- Real dead ends.
- Corners and centre.
- Wall coherence.
- Final verdict.

For the no-dead-end bonus:

```sh
python3 maze_analyzer.py maze.txt --max-dead-ends 0
```

## Performance and limits

The generator rejects grids containing more than 250,000 cells.

DFS uses an explicit stack, and the solver uses a deque, so neither operation
depends on Python call-stack depth.

Most core generation and validation operations scale with the number of cells
and grid edges. Braiding additionally examines closed edges and local `3x3`
windows.

Animation time can dominate total runtime because it intentionally sleeps
between operations. Set `DELAY=0` when visual speed is more important than
watching individual steps.

Very wide mazes may not fit inside a terminal even though their underlying data
is valid.

## Team and project management

This is a two-person project.

### Roles

- `alpturan` worked on configuration parsing and terminal visualization.
- `memalli` worked on the maze model, generation algorithms, validation,
  solving, output encoding, command-line integration, packaging, and project
  documentation.

### Initial plan

The initial implementation order was:

1. Configuration parsing.
2. Maze data model.
3. Generation algorithm.
4. Structural validation.
5. Shortest-path solving.
6. Output serialization.
7. Terminal visualization.
8. Packaging and documentation.

### How the plan evolved

Generation, validation, and solving were separated instead of placing all
behaviour in one large class.

This separation allowed:

- Prim to be added beside DFS.
- Both algorithms to use one validator.
- The visualizer to replay generic operations.
- Output encoding to remain independent from display.
- Maze structures to be consumed directly by future projects.

### What worked well

- One coherent wall-mutation API reduced asymmetric-wall errors.
- A common spanning-tree interface simplified multiple algorithms.
- Structural validation caught errors before file output.
- Seeded randomness made failures reproducible.
- The operation list connected the generator and animation cleanly.
- Keeping all generator imports inside `mazegen` kept the API independent.

### What could be improved

- Maintain and extend the local regression suite (not a submitted artifact).
- Add performance benchmarks for large mazes.
- Test more terminal sizes and terminal emulators.
- Improve terminal layout for very large grids.
- Add continuous integration for lint, type checking, and package builds.

### Tools used

- Git for version control.
- Make for common development commands.
- `uv` for dependency and package management.
- Virtual environments for dependency isolation.
- flake8 for Python style checks.
- mypy for static type checking.
- `maze_analyzer.py` for independent maze inspection.
- Python standard-library modules including `random`, `secrets`, `deque`,
  `dataclasses`, `enum`, `pathlib`, and `termios`.

## AI usage

AI tools were used as assistants for:

- Reviewing the subject requirements.
- Comparing required behaviour with the repository structure.
- Explaining graph concepts such as spanning trees and cycle rank.
- Reviewing configuration and error-handling cases.
- Suggesting validation matrices and edge cases.
- Explaining the Makefile and packaging workflow.
- Assisting with DFS/Prim integration review.
- Improving technical documentation.
- Fixing error handling, migrating packaging to uv, and preparing regression
  checks and clean-environment wheel verification for submission.

AI-generated suggestions were not treated as proof of correctness. The code was
reviewed against the project requirements and checked with static analysis,
structural validation, deterministic seeds, and the supplied analyzer.

Every team member is expected to understand and be able to explain the final
implementation during peer evaluation.

## Troubleshooting

### `uv` is not installed

Install `uv` using its official installation instructions, then run:

```sh
make install
```

### Configuration file not found

Check the path supplied as the only argument:

```sh
python3 a_maze_ing.py ./config.txt
```

### Missing mandatory key

Ensure the file contains all six mandatory keys:

```text
WIDTH
HEIGHT
ENTRY
EXIT
OUTPUT_FILE
PERFECT
```

### Entry or exit is outside the maze

For `WIDTH=20` and `HEIGHT=15`, valid coordinates satisfy:

```text
0 <= x < 20
0 <= y < 15
```

### The 42 pattern is omitted

The maze may be too small, the pattern may cover a protected cell, or no safe
placement may preserve connectivity and cycle capacity.

Use a grid of at least `9x7` and avoid placing entry or exit near the intended
central pattern area.

### Non-perfect generation is rejected

The dimensions may be too small or too thin to contain two independent cycles.

Increase both width and height.

### Colours are not visible

Use a terminal with ANSI TrueColor support. Redirected output and limited
terminal emulators may display raw escape sequences or simplified colours.

### Arrow keys do not change animation speed

Live speed control requires standard input to be attached to a compatible TTY.
It is intentionally disabled for non-interactive input.

### The maze is wider than the terminal

Reduce `WIDTH`, increase terminal width, or decrease terminal font size.

### Package imports fail after installation

Build the distribution again and test it inside a fresh virtual environment.
The reusable import should be:

```python
from mazegen import MazeGenerator
```

## Evaluation checklist

Before submission, verify each item:

- [ ] The first README line contains the required italicized sentence.
- [ ] `python3 a_maze_ing.py config.txt` works.
- [ ] The program accepts exactly one configuration argument.
- [ ] Missing and malformed configuration produces readable errors.
- [ ] The default configuration file is committed.
- [ ] `SEED` provides reproducible output.
- [ ] Perfect mode contains no loops.
- [ ] Non-perfect mode contains at least two independent loops.
- [ ] Every traversable corridor is connected.
- [ ] Four corners and centre are reachable in non-perfect mode.
- [ ] External borders are closed.
- [ ] Shared walls are coherent.
- [ ] No forbidden open `3x3` exists.
- [ ] The `42` pattern is visible when dimensions allow it.
- [ ] Small mazes print a clear pattern-omission message.
- [ ] Output uses one uppercase hexadecimal digit per cell.
- [ ] Output includes the blank separator line.
- [ ] Output includes entry, exit, and shortest-path lines.
- [ ] Every output line ends with a newline.
- [ ] Regeneration works.
- [ ] Shortest-path visibility can be toggled.
- [ ] Wall colours can be changed.
- [ ] `make install` works.
- [ ] `make run` works.
- [ ] `make debug` actually starts a debugger.
- [ ] `make clean` removes temporary caches.
- [ ] `make lint` passes.
- [ ] The reusable package builds successfully.
- [ ] A root-level `.whl` or `.tar.gz` exists for submission.
- [ ] The built package installs in a fresh environment.
- [ ] `LICENSE.md` is committed at repository root.
- [ ] The repository contains no accidental secrets or machine-specific files.
- [ ] Every team member can explain the algorithm and data representation.

## Resources

### Python documentation

- Python `random` module:
  <https://docs.python.org/3/library/random.html>
- Python `secrets` module:
  <https://docs.python.org/3/library/secrets.html>
- Python `dataclasses` module:
  <https://docs.python.org/3/library/dataclasses.html>
- Python `enum` module:
  <https://docs.python.org/3/library/enum.html>
- Python `collections.deque`:
  <https://docs.python.org/3/library/collections.html#collections.deque>
- Python `pathlib` module:
  <https://docs.python.org/3/library/pathlib.html>
- Python `typing` module:
  <https://docs.python.org/3/library/typing.html>
- Python `pdb` debugger:
  <https://docs.python.org/3/library/pdb.html>

### Packaging and tooling

- Python Packaging User Guide:
  <https://packaging.python.org/>
- `pyproject.toml` specification:
  <https://packaging.python.org/en/latest/specifications/pyproject-toml/>
- uv documentation:
  <https://docs.astral.sh/uv/>
- flake8 documentation:
  <https://flake8.pycqa.org/>
- mypy documentation:
  <https://mypy.readthedocs.io/>

### Algorithms and concepts

- Depth-first search.
- Breadth-first search.
- Randomized Prim's algorithm.
- Spanning trees.
- Connected components.
- Graph cycle rank.
- Perfect and braided maze generation.

## License

The reusable code is licensed under the GNU General Public License version 3.0.

See `LICENSE.md` for the complete license terms governing reuse and
redistribution.
