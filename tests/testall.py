"""Run a simple ASCII-board demonstration."""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mazegen.generator import Maze

generator = Maze(15, 15, (5,5), (10,10), 15)


generator.print_ascii_grid()
