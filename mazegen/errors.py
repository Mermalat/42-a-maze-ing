"""Exceptions raised by the maze algorithm package."""


class MazeError(Exception):
    """Base class for expected maze errors."""


class MazeGenerationError(MazeError):
    """Raised when the requested maze cannot be generated."""


class MazeValidationError(MazeError):
    """Raised when a maze violates a structural invariant."""


class MazeOutputError(MazeError):
    """Raised when maze output cannot be encoded or written."""
