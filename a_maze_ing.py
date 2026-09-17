#!/usr/bin/env python3
"""Command-line entry point for the A-Maze-ing project."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from mazegen import MazeError, MazeGenerator, write_output
from visualizer import ConfigError, MazeVisualizer, parse_config


def main(arguments: Sequence[str] | None = None) -> int:
    """Generate, save, and interactively display a configured maze."""
    args = list(sys.argv[1:] if arguments is None else arguments)
    if len(args) != 1:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1

    try:
        config = parse_config(args[0])
        generator = MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit=config.exit,
            seed=config.seed,
            perfect=config.perfect,
            algorithm=config.algorithm,
        )
        maze = generator.generate()
        write_output(maze, config.output_file)
        MazeVisualizer(
            generator, config.output_file, delay=config.delay
        ).run()
    except (ConfigError, MazeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
