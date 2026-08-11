"""
The Grid: holds pheromone strength per cell, handles decay and neighbor
lookups. This is a direct port of the Grid class from Phase 1 - same
behavior, just living in its own file now that the project has a real
backend structure.
"""

from app.simulation.config import (
    GRID_WIDTH, GRID_HEIGHT, OBSTACLES, MAX_PHEROMONE, PHEROMONE_DECAY,
)


class Grid:
    def __init__(self):
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        self.pheromone = [[0.0 for _ in range(self.height)] for _ in range(self.width)]

    def deposit(self, x, y, amount):
        self.pheromone[x][y] = min(self.pheromone[x][y] + amount, MAX_PHEROMONE)

    def decay_all(self):
        for x in range(self.width):
            for y in range(self.height):
                self.pheromone[x][y] *= PHEROMONE_DECAY

    def get_neighbors(self, x, y):
        neighbors = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in OBSTACLES:
                        neighbors.append((nx, ny))
        return neighbors
