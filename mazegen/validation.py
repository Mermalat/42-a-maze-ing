"""Structural checks for generated mazes."""

from __future__ import annotations

from dataclasses import dataclass

from mazegen.errors import MazeValidationError
from mazegen.model import ALL_WALLS, Coordinate, Direction, Maze
from mazegen.solver import shortest_path


@dataclass(frozen=True)
class ValidationReport:
    """Graph statistics collected from a valid maze."""

    traversable_cells: int
    open_edges: int
    cycle_rank: int
    dead_ends: int
    solution_length: int


def center_cell(width: int, height: int) -> Coordinate:
    """Select the right/bottom central cell for even dimensions."""
    return (width // 2, height // 2)


def _count_edges(maze: Maze) -> int:
    """Count each undirected open passage once."""
    edges = 0
    for cell in maze.traversable_cells():
        for direction in (Direction.EAST, Direction.SOUTH):
            dx, dy = direction.offset
            neighbor = (cell[0] + dx, cell[1] + dy)
            if maze.in_bounds(neighbor) and neighbor not in maze.blocked:
                edges += not maze.has_wall(cell, direction)
    return edges


def _window_is_open(maze: Maze, left: int, top: int) -> bool:
    """Return whether one 3-by-3 window has all internal walls open."""
    cells = {
        (x_pos, y_pos)
        for y_pos in range(top, top + 3)
        for x_pos in range(left, left + 3)
    }
    if cells & maze.blocked:
        return False
    horizontal = all(
        not maze.has_wall((x_pos, y_pos), Direction.EAST)
        for y_pos in range(top, top + 3)
        for x_pos in range(left, left + 2)
    )
    vertical = all(
        not maze.has_wall((x_pos, y_pos), Direction.SOUTH)
        for y_pos in range(top, top + 2)
        for x_pos in range(left, left + 3)
    )
    return horizontal and vertical


def has_open_3x3(maze: Maze) -> bool:
    """Return whether the maze contains a fully open 3-by-3 area."""
    return any(
        _window_is_open(maze, left, top)
        for top in range(maze.height - 2)
        for left in range(maze.width - 2)
    )


def validate_maze(maze: Maze) -> ValidationReport:
    """Verify wall, connectivity, path, and mode-specific invariants."""
    if len(maze.walls) != maze.height:
        raise MazeValidationError("wall grid height is incorrect")
    if any(len(row) != maze.width for row in maze.walls):
        raise MazeValidationError("wall grid width is incorrect")
    if maze.entry == maze.exit:
        raise MazeValidationError("entry and exit must differ")
    if not maze.in_bounds(maze.entry) or not maze.in_bounds(maze.exit):
        raise MazeValidationError("entry or exit is outside the maze")
    if maze.entry in maze.blocked or maze.exit in maze.blocked:
        raise MazeValidationError("entry or exit is blocked")

    for y_pos in range(maze.height):
        for x_pos in range(maze.width):
            cell = (x_pos, y_pos)
            value = maze.walls[y_pos][x_pos]
            if not 0 <= value <= ALL_WALLS:
                raise MazeValidationError(f"invalid wall value at {cell}")
            for neighbor, direction in maze.neighbors(cell):
                if maze.has_wall(cell, direction) != maze.has_wall(
                    neighbor, direction.opposite
                ):
                    raise MazeValidationError(
                        f"asymmetric shared wall at {cell}"
                    )

    for x_pos in range(maze.width):
        if not maze.has_wall((x_pos, 0), Direction.NORTH):
            raise MazeValidationError("north external border is open")
        if not maze.has_wall(
            (x_pos, maze.height - 1), Direction.SOUTH
        ):
            raise MazeValidationError("south external border is open")
    for y_pos in range(maze.height):
        if not maze.has_wall((0, y_pos), Direction.WEST):
            raise MazeValidationError("west external border is open")
        if not maze.has_wall(
            (maze.width - 1, y_pos), Direction.EAST
        ):
            raise MazeValidationError("east external border is open")

    for x_pos, y_pos in maze.blocked:
        if maze.walls[y_pos][x_pos] != ALL_WALLS:
            raise MazeValidationError("decorative cell is not fully closed")

    traversable = list(maze.traversable_cells())
    if len(traversable) < 2:
        raise MazeValidationError("maze has fewer than two traversable cells")
    reached: set[Coordinate] = set()
    pending = [traversable[0]]
    while pending:
        current = pending.pop()
        if current in reached:
            continue
        reached.add(current)
        pending.extend(
            neighbor
            for neighbor in maze.open_neighbors(current)
            if neighbor not in reached
        )
    if len(reached) != len(traversable):
        raise MazeValidationError("traversable cells are disconnected")
    degrees = [maze.degree(cell) for cell in traversable]
    if any(degree == 0 for degree in degrees):
        raise MazeValidationError("maze contains an isolated corridor cell")
    if has_open_3x3(maze):
        raise MazeValidationError("maze contains a fully open three-by-three")

    edges = _count_edges(maze)
    cycle_rank = edges - len(traversable) + 1
    if maze.perfect and cycle_rank != 0:
        raise MazeValidationError("perfect maze is not a tree")
    if not maze.perfect:
        required = {
            (0, 0),
            (maze.width - 1, 0),
            (0, maze.height - 1),
            (maze.width - 1, maze.height - 1),
            center_cell(maze.width, maze.height),
        }
        if required & maze.blocked:
            raise MazeValidationError("a required corner or center is blocked")
        if cycle_rank < 2:
            raise MazeValidationError(
                "non-perfect maze needs at least two independent cycles"
            )

    solution = shortest_path(maze)
    return ValidationReport(
        traversable_cells=len(traversable),
        open_edges=edges,
        cycle_rank=cycle_rank,
        dead_ends=sum(degree == 1 for degree in degrees),
        solution_length=len(solution) - 1,
    )


def window_is_open(maze: Maze, left: int, top: int) -> bool:
    """Expose the local 3-by-3 check to the generator."""
    return _window_is_open(maze, left, top)
