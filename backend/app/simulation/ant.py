"""
The Ant: same searching/returning logic as Phase 1, direct port.
"""

import random
from app.simulation.config import FOOD_POS, NEST_POS, PHEROMONE_DEPOSIT, HEURISTIC_POWER


class Ant:
    def __init__(self):
        self.x, self.y = NEST_POS
        self.has_food = False
        self.path_taken = [NEST_POS]
        self.return_path = []

    def _distance(self, pos, target):
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])

    def choose_next_move(self, grid):
        neighbors = grid.get_neighbors(self.x, self.y)
        weights = []
        for (nx, ny) in neighbors:
            pheromone_signal = 1.0 + grid.pheromone[nx][ny]
            dist_to_food = self._distance((nx, ny), FOOD_POS)
            heuristic_signal = (1.0 / (dist_to_food + 1)) ** HEURISTIC_POWER
            weights.append(pheromone_signal * heuristic_signal)
        return random.choices(neighbors, weights=weights, k=1)[0]

    def step(self, grid):
        """
        Returns (trip_length, completed_path) if this step just finished a
        round trip, otherwise (None, None). Same contract as Phase 1.
        """
        if not self.has_food:
            self.x, self.y = self.choose_next_move(grid)
            self.path_taken.append((self.x, self.y))

            if (self.x, self.y) == FOOD_POS:
                self.has_food = True
                self.return_path = list(reversed(self.path_taken))
                self.return_path.pop(0)

        else:
            self.x, self.y = self.return_path.pop(0)
            trip_length = len(self.path_taken) - 1
            amount = PHEROMONE_DEPOSIT / trip_length
            grid.deposit(self.x, self.y, amount)

            if (self.x, self.y) == NEST_POS:
                self.has_food = False
                completed_path = self.path_taken
                self.path_taken = [NEST_POS]
                self.return_path = []
                return trip_length, completed_path

        return None, None
