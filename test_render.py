# test_visualizer.py
from src.visualizer import MazeVisualizer
from mazegen.generator import MazeGenerator

# 3x3 Sahte labirent duvar verisi (0-15 bitmask)
# 15 = Dört tarafı kapalı
dummy_walls = [
    [9, 5, 3],   # y=0
    [8, 0, 2],   # y=1
    [12, 5, 6],  # y=2
]

entry = (0, 0)
exit_cell = (2, 2)
dummy_path = [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)]

generator = MazeGenerator(
    width=3,
    height=3,
    walls=dummy_walls,
    entry=entry,
    exit_cell=exit_cell,
    solution_path=dummy_path
)

viz = MazeVisualizer(generator)

# İlk Çizim
viz.render()

# Yolu gösterip tekrar çiz
viz.toggle_path()
viz.render()
