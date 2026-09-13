"""Tests for walls, generation modes, solving, and hexadecimal output."""

from __future__ import annotations

import re
import tempfile
import unittest
from collections import deque
from pathlib import Path

from mazegen import (
    ALL_WALLS,
    Direction,
    Maze,
    MazeGenerationError,
    MazeGenerator,
    has_open_3x3,
    serialize_maze,
    shortest_path,
    validate_maze,
    write_output,
)


def generated_maze(
    *, perfect: bool = True, seed: int = 42,
    width: int = 20, height: int = 15
) -> Maze:
    """Return a standard generated maze for a test."""
    return MazeGenerator(
        width=width,
        height=height,
        entry=(0, 0),
        exit=(width - 1, height - 1),
        seed=seed,
        perfect=perfect,
    ).generate()


class MazeAlgorithmTests(unittest.TestCase):
    """Exercise all algorithm responsibilities assigned to this module."""

    def test_seed_is_deterministic(self) -> None:
        """Equal seeds create equal wall grids."""
        self.assertEqual(
            generated_maze(seed=123).walls,
            generated_maze(seed=123).walls,
        )
        self.assertNotEqual(
            generated_maze(seed=123).walls,
            generated_maze(seed=124).walls,
        )

    def test_wall_symmetry_and_closed_borders(self) -> None:
        """Shared walls agree and no external border is opened."""
        maze = generated_maze(perfect=False)
        for cell in maze.traversable_cells():
            for neighbor, direction in maze.neighbors(cell):
                self.assertEqual(
                    maze.has_wall(cell, direction),
                    maze.has_wall(neighbor, direction.opposite),
                )
        self.assertTrue(
            all(
                maze.has_wall((x_pos, 0), Direction.NORTH)
                for x_pos in range(maze.width)
            )
        )
        self.assertTrue(
            all(
                maze.has_wall(
                    (x_pos, maze.height - 1), Direction.SOUTH
                )
                for x_pos in range(maze.width)
            )
        )

    def test_perfect_maze_is_connected_tree(self) -> None:
        """Perfect mode has zero cycles and exactly V-1 edges."""
        report = validate_maze(generated_maze(perfect=True))
        self.assertEqual(report.cycle_rank, 0)
        self.assertEqual(report.open_edges, report.traversable_cells - 1)

    def test_non_perfect_maze_has_many_routes(self) -> None:
        """Non-perfect mode has at least two independent cycles."""
        report = validate_maze(generated_maze(perfect=False))
        self.assertGreaterEqual(report.cycle_rank, 2)

    def test_no_open_three_by_three_area(self) -> None:
        """Neither mode creates a fully open 3-by-3 region."""
        for perfect in (True, False):
            for seed in range(10):
                with self.subTest(perfect=perfect, seed=seed):
                    self.assertFalse(
                        has_open_3x3(
                            generated_maze(perfect=perfect, seed=seed)
                        )
                    )

    def test_pattern_cells_are_f_and_not_route_cells(self) -> None:
        """All decorative cells are fully closed and avoided by the solver."""
        maze = generated_maze()
        route = set(shortest_path(maze))
        self.assertEqual(len(maze.blocked), 20)
        self.assertFalse(route & maze.blocked)
        for x_pos, y_pos in maze.blocked:
            self.assertEqual(maze.walls[y_pos][x_pos], ALL_WALLS)

    def test_small_rectangular_maze_without_pattern(self) -> None:
        """Small rectangular mazes remain valid when 42 cannot fit."""
        generator = MazeGenerator(4, 7, (0, 0), (3, 6), seed=8)
        maze = generator.generate()
        self.assertFalse(maze.blocked)
        self.assertTrue(generator.diagnostics)
        validate_maze(maze)

    def test_shortest_path_follows_open_walls(self) -> None:
        """The BFS solution connects the endpoints without crossing walls."""
        maze = generated_maze(perfect=False, seed=99)
        route = shortest_path(maze)
        self.assertEqual(route[0], maze.entry)
        self.assertEqual(route[-1], maze.exit)
        for first, second in zip(route, route[1:]):
            self.assertIn(second, maze.open_neighbors(first))
        distances: dict[tuple[int, int], int] = {maze.entry: 0}
        pending: deque[tuple[int, int]] = deque([maze.entry])
        while pending:
            current = pending.popleft()
            for neighbor in maze.open_neighbors(current):
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    pending.append(neighbor)
        self.assertEqual(len(route) - 1, distances[maze.exit])

    def test_invalid_requests_are_rejected(self) -> None:
        """Bad dimensions and coordinates raise generation errors."""
        invalid = (
            (0, 5, (0, 0), (0, 1), True),
            (5, 5, (-1, 0), (4, 4), True),
            (5, 5, (0, 0), (5, 4), True),
            (5, 5, (2, 2), (2, 2), True),
            (2, 2, (0, 0), (1, 1), False),
        )
        for width, height, entry, exit_cell, perfect in invalid:
            with self.subTest(width=width, height=height):
                with self.assertRaises(MazeGenerationError):
                    MazeGenerator(
                        width,
                        height,
                        entry,
                        exit_cell,
                        perfect=perfect,
                    )

    def test_exact_hexadecimal_output(self) -> None:
        """Output has uppercase cells, footer, solution, and final newline."""
        maze = generated_maze(width=10, height=8)
        content = serialize_maze(maze)
        lines = content.splitlines()
        self.assertTrue(content.endswith("\n"))
        self.assertEqual(len(lines), maze.height + 4)
        for row in lines[:maze.height]:
            self.assertEqual(len(row), maze.width)
            self.assertIsNotNone(re.fullmatch(r"[0-9A-F]+", row))
        self.assertEqual(lines[maze.height], "")
        self.assertEqual(lines[maze.height + 1], "0,0")
        self.assertEqual(lines[maze.height + 2], "9,7")
        self.assertIsNotNone(
            re.fullmatch(r"[NESW]+", lines[maze.height + 3])
        )

    def test_known_masks_and_file_writer(self) -> None:
        """One horizontal passage encodes as D7 and writes exact bytes."""
        maze = generated_maze(width=2, height=1, seed=5)
        expected = "D7\n\n0,0\n1,0\nE\n"
        self.assertEqual(serialize_maze(maze), expected)
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "output_maze.txt"
            write_output(maze, output_path)
            self.assertEqual(
                output_path.read_text(encoding="ascii"), expected
            )


if __name__ == "__main__":
    unittest.main()
