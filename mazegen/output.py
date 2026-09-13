"""Required hexadecimal maze output encoding."""

from __future__ import annotations

from pathlib import Path

from mazegen.errors import MazeOutputError
from mazegen.model import Coordinate, Maze
from mazegen.solver import path_to_directions, shortest_path
from mazegen.validation import validate_maze


def serialize_maze(
    maze: Maze, solution: list[Coordinate] | None = None
) -> str:
    """Return the exact grid, coordinate, and shortest-path file content."""
    validate_maze(maze)
    route = shortest_path(maze) if solution is None else solution
    canonical = shortest_path(maze)
    if not route or route[0] != maze.entry or route[-1] != maze.exit:
        raise MazeOutputError("solution must connect entry to exit")
    if len(route) != len(canonical):
        raise MazeOutputError("solution is not a shortest path")
    for first, second in zip(route, route[1:]):
        if second not in maze.open_neighbors(first):
            raise MazeOutputError("solution crosses a closed wall")
    lines = maze.to_hex_lines() + [
        "",
        f"{maze.entry[0]},{maze.entry[1]}",
        f"{maze.exit[0]},{maze.exit[1]}",
        path_to_directions(route),
    ]
    return "\n".join(lines) + "\n"


def write_output(
    maze: Maze,
    path: str | Path = "output_maze.txt",
    solution: list[Coordinate] | None = None,
) -> None:
    """Write a maze to ``output_maze.txt`` or another selected path."""
    output_path = Path(path)
    content = serialize_maze(maze, solution)
    try:
        with output_path.open("w", encoding="ascii", newline="\n") as stream:
            stream.write(content)
    except PermissionError as exc:
        raise MazeOutputError(
            f"permission denied writing {output_path}"
        ) from exc
    except OSError as exc:
        raise MazeOutputError(f"cannot write {output_path}: {exc}") from exc
