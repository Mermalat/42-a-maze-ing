"""Perfect and loop-rich maze generation algorithms."""

from __future__ import annotations

import random
import secrets

from mazegen.errors import MazeGenerationError
from mazegen.model import (
    ALL_WALLS,
    CellOperation,
    Coordinate,
    Direction,
    Maze,
    Operation,
    OperationList,
)
from mazegen.solver import shortest_path
from mazegen.validation import (
    ValidationReport,
    center_cell,
    validate_maze,
    window_is_open,
)

PATTERN: tuple[str, ...] = (
    "X.X.XXX",
    "X.X...X",
    "XXX.XXX",
    "..X.X..",
    "..X.XXX",
)
PATTERN_WIDTH = len(PATTERN[0])
PATTERN_HEIGHT = len(PATTERN)
MAX_CELLS = 250_000
SUPPORTED_ALGORITHMS = frozenset({"dfs", "prim"})


class MazeGenerator:
    """Generate deterministic perfect or non-perfect mazes."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: Coordinate,
        exit: Coordinate,
        seed: int | None = None,
        perfect: bool = False,
        include_pattern: bool = True,
        algorithm: str = "dfs",
    ) -> None:
        """Store and validate generation parameters.

        Args:
            width: Positive number of columns.
            height: Positive number of rows; at most 250,000 total cells.
            entry: Starting cell as a zero-based (x, y) tuple.
            exit: Different destination cell inside the grid.
            seed: Integer seed, or None to choose a random 64-bit seed.
            perfect: Whether to keep a tree instead of adding loops.
            include_pattern: Whether to reserve closed cells spelling 42.
            algorithm: Either dfs or prim, case-insensitively.

        Raises:
            MazeGenerationError: If the settings are invalid or impossible.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.seed = secrets.randbits(64) if seed is None else seed
        self.perfect = perfect
        self.include_pattern = include_pattern
        self.algorithm = (
            algorithm.lower() if isinstance(algorithm, str) else algorithm
        )
        self.maze: Maze | None = None
        self.operation_list: OperationList = []
        self.report: ValidationReport | None = None
        self.diagnostics: list[str] = []
        self._validate_arguments()

    def _validate_arguments(self) -> None:
        """Reject invalid coordinates, modes, and impossible dimensions."""
        if isinstance(self.width, bool) or not isinstance(self.width, int):
            raise MazeGenerationError("width must be an integer")
        if isinstance(self.height, bool) or not isinstance(self.height, int):
            raise MazeGenerationError("height must be an integer")
        if self.width <= 0 or self.height <= 0:
            raise MazeGenerationError("width and height must be positive")
        if self.width * self.height > MAX_CELLS:
            raise MazeGenerationError(
                f"maze cannot exceed {MAX_CELLS} cells"
            )
        if self.width * self.height < 2:
            raise MazeGenerationError("maze needs at least two cells")
        for label, cell in (("entry", self.entry), ("exit", self.exit)):
            if not isinstance(cell, tuple) or len(cell) != 2:
                raise MazeGenerationError(f"{label} must be an x,y pair")
            if any(
                isinstance(value, bool) or not isinstance(value, int)
                for value in cell
            ):
                raise MazeGenerationError(
                    f"{label} coordinates must be integers"
                )
            if not self._in_bounds(cell):
                raise MazeGenerationError(f"{label} is outside the maze")
        if self.entry == self.exit:
            raise MazeGenerationError("entry and exit must be different")
        if not isinstance(self.seed, int) or isinstance(self.seed, bool):
            raise MazeGenerationError("seed must be an integer")
        if not isinstance(self.perfect, bool):
            raise MazeGenerationError("perfect must be a boolean")
        if not isinstance(self.include_pattern, bool):
            raise MazeGenerationError("include_pattern must be a boolean")
        if (
            not isinstance(self.algorithm, str)
            or self.algorithm not in SUPPORTED_ALGORITHMS
        ):
            choices = ", ".join(sorted(SUPPORTED_ALGORITHMS))
            raise MazeGenerationError(
                f"algorithm must be one of: {choices}"
            )
        if not self.perfect and self._maximum_cycle_rank(set()) < 2:
            raise MazeGenerationError(
                "dimensions cannot contain two independent cycles"
            )

    def _in_bounds(self, cell: Coordinate) -> bool:
        """Return whether a cell lies inside the requested grid."""
        return (
            0 <= cell[0] < self.width
            and 0 <= cell[1] < self.height
        )

    def _grid_neighbors(
        self, cell: Coordinate, blocked: set[Coordinate]
    ) -> list[tuple[Coordinate, Direction]]:
        """Return available grid neighbors in stable direction order."""
        result: list[tuple[Coordinate, Direction]] = []
        for direction in Direction:
            dx, dy = direction.offset
            neighbor = (cell[0] + dx, cell[1] + dy)
            if self._in_bounds(neighbor) and neighbor not in blocked:
                result.append((neighbor, direction))
        return result

    def _maximum_cycle_rank(self, blocked: set[Coordinate]) -> int:
        """Return the cycle rank of the fully open available grid."""
        vertices = self.width * self.height - len(blocked)
        edges = 0
        for y_pos in range(self.height):
            for x_pos in range(self.width):
                cell = (x_pos, y_pos)
                if cell in blocked:
                    continue
                if x_pos + 1 < self.width:
                    edges += (x_pos + 1, y_pos) not in blocked
                if y_pos + 1 < self.height:
                    edges += (x_pos, y_pos + 1) not in blocked
        return edges - vertices + 1

    def _cells_are_connected(self, blocked: set[Coordinate]) -> bool:
        """Check connectivity before accepting a decorative pattern."""
        cells = {
            (x_pos, y_pos)
            for y_pos in range(self.height)
            for x_pos in range(self.width)
            if (x_pos, y_pos) not in blocked
        }
        if not cells:
            return False
        reached: set[Coordinate] = set()
        pending = [next(iter(cells))]
        while pending:
            current = pending.pop()
            if current in reached:
                continue
            reached.add(current)
            pending.extend(
                neighbor
                for neighbor, _direction in self._grid_neighbors(
                    current, blocked
                )
                if neighbor not in reached
            )
        return reached == cells

    @staticmethod
    def _pattern_at(left: int, top: int) -> set[Coordinate]:
        """Return the X coordinates of a translated 42 pattern."""
        return {
            (left + x_pos, top + y_pos)
            for y_pos, row in enumerate(PATTERN)
            for x_pos, marker in enumerate(row)
            if marker == "X"
        }

    def _choose_pattern(self) -> set[Coordinate]:
        """Find a safe pattern placement nearest the maze center."""
        if not self.include_pattern:
            return set()
        if self.width < PATTERN_WIDTH + 2 or self.height < PATTERN_HEIGHT + 2:
            self.diagnostics.append(
                "42 pattern omitted: maze is too small for a safe margin"
            )
            return set()
        preferred = (
            (self.width - PATTERN_WIDTH) // 2,
            (self.height - PATTERN_HEIGHT) // 2,
        )
        origins = [
            (left, top)
            for top in range(1, self.height - PATTERN_HEIGHT)
            for left in range(1, self.width - PATTERN_WIDTH)
        ]
        origins.sort(
            key=lambda origin: (
                abs(origin[0] - preferred[0])
                + abs(origin[1] - preferred[1]),
                origin[1],
                origin[0],
            )
        )
        protected = {
            self.entry,
            self.exit,
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
            center_cell(self.width, self.height),
        }
        for left, top in origins:
            blocked = self._pattern_at(left, top)
            if blocked & protected or not self._cells_are_connected(blocked):
                continue
            if not self.perfect and self._maximum_cycle_rank(blocked) < 2:
                continue
            return blocked
        self.diagnostics.append(
            "42 pattern omitted: no safe connected placement was found"
        )
        return set()

    def _carve_tree_dfs(self, maze: Maze, rng: random.Random) -> None:
        """Carve a randomized depth-first spanning tree."""
        cells = list(maze.traversable_cells())
        start = rng.choice(cells)
        reached = {start}
        stack = [start]
        blocked = set(maze.blocked)
        while stack:
            current = stack[-1]
            candidates = [
                item
                for item in self._grid_neighbors(current, blocked)
                if item[0] not in reached
            ]
            if not candidates:
                stack.pop()
                continue
            neighbor, direction = rng.choice(candidates)
            self._remove_wall(maze, current, direction)
            reached.add(neighbor)
            stack.append(neighbor)
        if len(reached) != len(cells):
            raise MazeGenerationError("could not connect every corridor cell")

    def _carve_tree_prim(self, maze: Maze, rng: random.Random) -> None:
        """Carve a spanning tree using randomized Prim's algorithm."""
        cells = list(maze.traversable_cells())
        start = rng.choice(cells)
        reached = {start}
        blocked = set(maze.blocked)
        frontier = [
            (start, neighbor, direction)
            for neighbor, direction in self._grid_neighbors(start, blocked)
        ]

        while frontier:
            index = rng.randrange(len(frontier))
            cell, neighbor, direction = frontier[index]
            frontier[index] = frontier[-1]
            frontier.pop()
            if neighbor in reached:
                continue
            self._remove_wall(maze, cell, direction)
            reached.add(neighbor)
            frontier.extend(
                (neighbor, candidate, candidate_direction)
                for candidate, candidate_direction in self._grid_neighbors(
                    neighbor, blocked
                )
                if candidate not in reached
            )

        if len(reached) != len(cells):
            raise MazeGenerationError("could not connect every corridor cell")

    def _carve_tree(self, maze: Maze, rng: random.Random) -> None:
        """Carve a spanning tree with the configured algorithm."""
        if self.algorithm == "prim":
            self._carve_tree_prim(maze, rng)
        else:
            self._carve_tree_dfs(maze, rng)

    @staticmethod
    def _closed_edges(
        maze: Maze,
    ) -> list[tuple[Coordinate, Direction]]:
        """Return each closed shared wall exactly once."""
        edges: list[tuple[Coordinate, Direction]] = []
        for cell in maze.traversable_cells():
            for direction in (Direction.EAST, Direction.SOUTH):
                dx, dy = direction.offset
                neighbor = (cell[0] + dx, cell[1] + dy)
                if (
                    maze.in_bounds(neighbor)
                    and neighbor not in maze.blocked
                    and maze.has_wall(cell, direction)
                ):
                    edges.append((cell, direction))
        return edges

    def _opening_creates_open_3x3(
        self, maze: Maze, cell: Coordinate, direction: Direction
    ) -> bool:
        """Test affected 3-by-3 windows before opening a wall."""
        dx, dy = direction.offset
        neighbor = (cell[0] + dx, cell[1] + dy)
        maze.remove_wall(cell, direction)
        min_x = min(cell[0], neighbor[0])
        max_x = max(cell[0], neighbor[0])
        min_y = min(cell[1], neighbor[1])
        max_y = max(cell[1], neighbor[1])
        creates_open_area = any(
            window_is_open(maze, left, top)
            for top in range(
                max(0, max_y - 2),
                min(min_y, maze.height - 3) + 1,
            )
            for left in range(
                max(0, max_x - 2),
                min(min_x, maze.width - 3) + 1,
            )
        )
        maze.add_wall(cell, direction)
        return creates_open_area

    def _try_open(
        self, maze: Maze, cell: Coordinate, direction: Direction
    ) -> bool:
        """Open a wall unless it violates the 3-by-3 invariant."""
        if not maze.has_wall(cell, direction):
            return False
        if self._opening_creates_open_3x3(maze, cell, direction):
            return False
        self._remove_wall(maze, cell, direction)
        return True

    def _remove_wall(
        self, maze: Maze, cell: Coordinate, direction: Direction
    ) -> None:
        """Open a passage and record the permanent generation operation."""
        dx, dy = direction.offset
        target = (cell[0] + dx, cell[1] + dy)
        maze.remove_wall(cell, direction)
        self.operation_list.append(
            CellOperation(cell, target, Operation.REMOVE_WALL)
        )

    def _braid(self, maze: Maze, rng: random.Random) -> None:
        """Reduce dead ends and create several independent cycles."""
        opened = 0
        for _pass_number in range(3):
            dead_ends = [
                cell
                for cell in maze.traversable_cells()
                if maze.degree(cell) == 1
            ]
            rng.shuffle(dead_ends)
            changed = False
            for cell in dead_ends:
                if maze.degree(cell) != 1:
                    continue
                candidates = [
                    (neighbor, direction)
                    for neighbor, direction in maze.neighbors(cell)
                    if neighbor not in maze.blocked
                    and maze.has_wall(cell, direction)
                ]
                rng.shuffle(candidates)
                candidates.sort(key=lambda item: maze.degree(item[0]))
                for _neighbor, direction in candidates:
                    if self._try_open(maze, cell, direction):
                        opened += 1
                        changed = True
                        break
            if not changed:
                break

        target_rank = max(
            2, sum(1 for _cell in maze.traversable_cells()) // 12
        )
        remaining = self._closed_edges(maze)
        rng.shuffle(remaining)
        for cell, direction in remaining:
            if opened >= target_rank:
                break
            if self._try_open(maze, cell, direction):
                opened += 1

    def generate(self) -> Maze:
        """Generate and validate a maze using the current settings.

        Returns:
            A Maze with walls, endpoints, seed and decorative cells.

        Raises:
            MazeGenerationError: If the current parameters are impossible.
            MazeValidationError: If the generated structure is invalid.
        """
        self._validate_arguments()
        self.diagnostics.clear()
        self.operation_list.clear()
        blocked = self._choose_pattern()
        maze = Maze(
            width=self.width,
            height=self.height,
            entry=self.entry,
            exit=self.exit,
            seed=self.seed,
            perfect=self.perfect,
            walls=[
                [ALL_WALLS for _x_pos in range(self.width)]
                for _y_pos in range(self.height)
            ],
            blocked=frozenset(blocked),
        )
        rng = random.Random(self.seed)
        self._carve_tree(maze, rng)
        if not self.perfect:
            self._braid(maze, rng)
        self.report = validate_maze(maze)
        self.maze = maze
        return maze

    def shortest_path(self) -> list[Coordinate]:
        """Return the shortest coordinate route, including both endpoints.

        Raises:
            MazeGenerationError: If generate has not succeeded yet.
        """
        if self.maze is None:
            raise MazeGenerationError("generate the maze before solving it")
        return shortest_path(self.maze)
