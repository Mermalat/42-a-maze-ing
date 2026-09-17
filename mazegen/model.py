"""Maze grid representation and coherent wall operations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntFlag
from typing import Iterator, TypeAlias

Coordinate = tuple[int, int]


class Direction(IntFlag):
    """Wall bits used by the required hexadecimal representation."""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    @property
    def opposite(self) -> "Direction":
        """Return the same shared wall as seen from the next cell."""
        return OPPOSITES[self]

    @property
    def offset(self) -> Coordinate:
        """Return the x/y movement associated with this direction."""
        return OFFSETS[self]

    @property
    def letter(self) -> str:
        """Return the direction's one-letter solution encoding."""
        return LETTERS[self]


OPPOSITES: dict[Direction, Direction] = {
    Direction.NORTH: Direction.SOUTH,
    Direction.EAST: Direction.WEST,
    Direction.SOUTH: Direction.NORTH,
    Direction.WEST: Direction.EAST,
}
OFFSETS: dict[Direction, Coordinate] = {
    Direction.NORTH: (0, -1),
    Direction.EAST: (1, 0),
    Direction.SOUTH: (0, 1),
    Direction.WEST: (-1, 0),
}
LETTERS: dict[Direction, str] = {
    Direction.NORTH: "N",
    Direction.EAST: "E",
    Direction.SOUTH: "S",
    Direction.WEST: "W",
}
ALL_WALLS = 0xF


class Operation(str, Enum):
    """Supported mutations recorded while a maze is generated."""

    REMOVE_WALL = "remove_wall"


@dataclass(frozen=True)
class CellOperation:
    """Describe one mutation between two adjacent maze cells."""

    source: Coordinate
    target: Coordinate
    operation: Operation

    @property
    def direction(self) -> Direction:
        """Return the direction from the source cell to the target cell."""
        offset = (
            self.target[0] - self.source[0],
            self.target[1] - self.source[1],
        )
        for direction in Direction:
            if direction.offset == offset:
                return direction
        raise ValueError("cell operation endpoints must be adjacent")

    def apply(self, maze: "Maze") -> None:
        """Apply this recorded mutation to a maze."""
        if self.operation is Operation.REMOVE_WALL:
            maze.remove_wall(self.source, self.direction)
            return
        raise ValueError(f"unsupported cell operation: {self.operation}")


OperationList: TypeAlias = list[CellOperation]


@dataclass(frozen=True)
class Maze:
    """A generated rectangular maze.

    Coordinates are always ``(x, y)``. Each wall value uses bits N=1, E=2,
    S=4, and W=8; a set bit means the wall is closed.
    """

    width: int
    height: int
    entry: Coordinate
    exit: Coordinate
    seed: int
    perfect: bool
    walls: list[list[int]]
    blocked: frozenset[Coordinate]

    def in_bounds(self, cell: Coordinate) -> bool:
        """Return whether a cell lies inside the grid."""
        x_pos, y_pos = cell
        return 0 <= x_pos < self.width and 0 <= y_pos < self.height

    def traversable_cells(self) -> Iterator[Coordinate]:
        """Yield cells that are not closed decorative cells."""
        for y_pos in range(self.height):
            for x_pos in range(self.width):
                cell = (x_pos, y_pos)
                if cell not in self.blocked:
                    yield cell

    def neighbors(
        self, cell: Coordinate
    ) -> Iterator[tuple[Coordinate, Direction]]:
        """Yield each in-bounds orthogonal neighbor and its direction."""
        x_pos, y_pos = cell
        for direction in Direction:
            dx, dy = direction.offset
            neighbor = (x_pos + dx, y_pos + dy)
            if self.in_bounds(neighbor):
                yield neighbor, direction

    def has_wall(self, cell: Coordinate, direction: Direction) -> bool:
        """Return whether one wall of a cell is closed."""
        if not self.in_bounds(cell):
            raise ValueError(f"cell is outside the maze: {cell}")
        x_pos, y_pos = cell
        return bool(self.walls[y_pos][x_pos] & direction)

    def remove_wall(self, cell: Coordinate, direction: Direction) -> None:
        """Open a shared wall on both adjacent cells."""
        if not self.in_bounds(cell):
            raise ValueError(f"cell is outside the maze: {cell}")
        dx, dy = direction.offset
        neighbor = (cell[0] + dx, cell[1] + dy)
        if not self.in_bounds(neighbor):
            raise ValueError("cannot open an external border")
        if cell in self.blocked or neighbor in self.blocked:
            raise ValueError("cannot open a decorative closed cell")
        self.walls[cell[1]][cell[0]] &= ~int(direction)
        self.walls[neighbor[1]][neighbor[0]] &= ~int(direction.opposite)

    def add_wall(self, cell: Coordinate, direction: Direction) -> None:
        """Close a shared wall on both adjacent cells."""
        if not self.in_bounds(cell):
            raise ValueError(f"cell is outside the maze: {cell}")
        dx, dy = direction.offset
        neighbor = (cell[0] + dx, cell[1] + dy)
        if not self.in_bounds(neighbor):
            raise ValueError("cannot address an external shared wall")
        self.walls[cell[1]][cell[0]] |= int(direction)
        self.walls[neighbor[1]][neighbor[0]] |= int(direction.opposite)

    def open_neighbors(self, cell: Coordinate) -> Iterator[Coordinate]:
        """Yield traversable neighbors joined by an open passage."""
        for neighbor, direction in self.neighbors(cell):
            if neighbor not in self.blocked and not self.has_wall(
                cell, direction
            ):
                yield neighbor

    def degree(self, cell: Coordinate) -> int:
        """Return the number of open passages incident to a cell."""
        return sum(1 for _neighbor in self.open_neighbors(cell))

    def to_hex_lines(self) -> list[str]:
        """Return the maze grid as uppercase hexadecimal rows."""
        return [
            "".join(format(value, "X") for value in row)
            for row in self.walls
        ]
