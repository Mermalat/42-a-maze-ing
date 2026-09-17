"""Public API for maze generation, solving, and output."""

from mazegen.errors import (
    MazeError,
    MazeGenerationError,
    MazeOutputError,
    MazeValidationError,
)
from mazegen.generator import MazeGenerator
from mazegen.model import (
    ALL_WALLS,
    CellOperation,
    Coordinate,
    Direction,
    Maze,
    Operation,
    OperationList,
)
from mazegen.output import serialize_maze, write_output
from mazegen.solver import path_to_directions, shortest_path
from mazegen.validation import ValidationReport, has_open_3x3, validate_maze

__all__ = [
    "ALL_WALLS",
    "CellOperation",
    "Coordinate",
    "Direction",
    "Maze",
    "MazeError",
    "MazeGenerationError",
    "MazeGenerator",
    "MazeOutputError",
    "MazeValidationError",
    "Operation",
    "OperationList",
    "ValidationReport",
    "has_open_3x3",
    "path_to_directions",
    "serialize_maze",
    "shortest_path",
    "validate_maze",
    "write_output",
]
