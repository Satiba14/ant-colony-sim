"""
Configuration constants for the simulation.

Identical values to Phase 1 (simulation.py) and Phase 2 (visualization.html) -
we are RELOCATING the logic here, not changing it. If Phase 1/2 already
proved these numbers converge correctly, changing them now would make it
harder to tell whether a bug is in the port or a new problem.
"""

GRID_WIDTH = 20
GRID_HEIGHT = 20
NEST_POS = (0, 10)
FOOD_POS = (19, 10)

WALL_X = 10
SHORT_GAP_Y = {9, 10, 11}
LONG_GAP_Y = {0, 1}
OBSTACLES = {
    (WALL_X, y) for y in range(GRID_HEIGHT)
    if y not in SHORT_GAP_Y and y not in LONG_GAP_Y
}

PHEROMONE_DECAY = 0.95
PHEROMONE_DEPOSIT = 5.0
MAX_PHEROMONE = 40.0
HEURISTIC_POWER = 2
ELITE_BOOST = 20.0

DEFAULT_NUM_ANTS = 30
