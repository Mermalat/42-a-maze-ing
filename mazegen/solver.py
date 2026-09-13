"""Shortest-path solving kept separate from maze generation."""

from __future__ import annotations

from collections import deque

from mazegen.errors import MazeValidationError
from mazegen.model import Coordinate, Direction, Maze


def shortest_path(
    maze: Maze,
    start: Coordinate | None = None,
    goal: Coordinate | None = None,
) -> list[Coordinate]:
    """Find a shortest route with breadth-first search.

    The returned path includes both endpoints. Breadth-first search guarantees
    minimal length because every passage has equal cost.
    """
    origin = maze.entry if start is None else start
    destination = maze.exit if goal is None else goal
    if not maze.in_bounds(origin) or not maze.in_bounds(destination):
        raise MazeValidationError("solution endpoint is outside the maze")
    if origin in maze.blocked or destination in maze.blocked:
        raise MazeValidationError("solution endpoint is a closed cell")

    pending: deque[Coordinate] = deque([origin])
    previous: dict[Coordinate, Coordinate | None] = {origin: None}
    while pending:
        current = pending.popleft()
        if current == destination:
            break
        for neighbor in maze.open_neighbors(current):
            if neighbor not in previous:
                previous[neighbor] = current
                pending.append(neighbor)

    if destination not in previous:
        raise MazeValidationError(
            f"no route exists from {origin} to {destination}"
        )
    path: list[Coordinate] = []
    cursor: Coordinate | None = destination
    while cursor is not None:
        path.append(cursor)
        cursor = previous[cursor]
    path.reverse()
    return path


def path_to_directions(path: list[Coordinate]) -> str:
    """Encode a coordinate path using only N, E, S, and W."""
    direction_for_offset = {
        direction.offset: direction.letter for direction in Direction
    }
    encoded: list[str] = []
    for first, second in zip(path, path[1:]):
        offset = (second[0] - first[0], second[1] - first[1])
        try:
            encoded.append(direction_for_offset[offset])
        except KeyError as exc:
            raise MazeValidationError(
                "solution path contains non-adjacent cells"
            ) from exc
    return "".join(encoded)
