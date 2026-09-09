from collections.abc import Iterator
import time


AsciiCell = tuple[int, int, str]


class Maze:
    def __init__(self, width: int, height: int, startsAt: tuple[int, int], endsAt: tuple[int, int], seed: int,  delay: float = 0.01) -> None:
        self.width: int = width
        self.height: int = height
        self.delay: float = delay
        self.startsAt: tuple[int, int] = startsAt
        self.endsAt: tuple[int, int] = endsAt
        self.seed: int = seed
        self.solvepath : str

    def iter_ascii_grid(self) -> Iterator[str]:
        """Yield the board after placing each ASCII cell.

        The caller can render every yielded board immediately, or wait between
        steps, so the board appears one cell at a time.
        """
        board: list[list[str]] = [
            [" "] * self.width for _ in range(self.height)
        ]

        for row, column, cell in self.iter_ascii_cells():
            board[row][column] = cell
            yield "\n".join("".join(line) for line in board)

    def iter_ascii_cells(self) -> Iterator[AsciiCell]:
        """Yield one cell at a time; maze rules will replace this later."""
        for row in range(self.height):
            for column in range(self.width):
                if column == 1 and row == 1 or column == 13 and row == 13:
                    yield row, column, "   "
                else:
                    yield row, column, "███"

    def print_ascii_grid(self) -> None:
        """Print the ASCII board one character at a time."""
        if self.delay < 0:
            raise ValueError("delay must be zero or greater")


        for _, column, cell in self.iter_ascii_cells():
            line_end = "\n" if column == self.width - 1 else ""
            print(cell, end=line_end, flush=True)
            time.sleep(self.delay)
