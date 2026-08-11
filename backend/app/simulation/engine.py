"""
The Engine: owns one running simulation (a Grid + a list of Ants) and knows
how to advance it one tick and serialize its current state to plain
dicts/lists that can be sent over the WebSocket as JSON.

This is the one genuinely NEW piece in Phase 3 - Phase 1/2 never needed to
serialize state because everything lived in one process. Here the backend
and the browser are separate processes talking over a socket, so state has
to be converted to something JSON can carry (no Python objects, no sets/
tuples-as-dict-keys - plain lists and numbers only).
"""

from app.simulation.grid import Grid
from app.simulation.ant import Ant
from app.simulation.config import (
    NEST_POS, FOOD_POS, WALL_X, SHORT_GAP_Y, LONG_GAP_Y, OBSTACLES,
    ELITE_BOOST, DEFAULT_NUM_ANTS,
)


class SimulationEngine:
    def __init__(self, num_ants=DEFAULT_NUM_ANTS):
        self.num_ants = num_ants
        self.reset()

    def reset(self, num_ants=None):
        if num_ants is not None:
            self.num_ants = num_ants
        self.grid = Grid()
        self.ants = [Ant() for _ in range(self.num_ants)]
        self.tick_count = 0
        self.trips_completed = 0
        self.best_length = None
        self.best_path = None
        self.gap_history = []  # rolling list of 'short'/'long', last 20

    def _which_gap(self, path):
        for (px, py) in path:
            if px == WALL_X and py in SHORT_GAP_Y:
                return 'short'
            if px == WALL_X and py in LONG_GAP_Y:
                return 'long'
        return 'unknown'

    def tick(self):
        """Advance the simulation by exactly one tick."""
        for ant in self.ants:
            finished_length, finished_path = ant.step(self.grid)
            if finished_length is not None:
                self.trips_completed += 1
                self.gap_history.append(self._which_gap(finished_path))
                if len(self.gap_history) > 20:
                    self.gap_history.pop(0)
                if self.best_length is None or finished_length < self.best_length:
                    self.best_length = finished_length
                    self.best_path = finished_path

        if self.best_path is not None:
            elite_amount = ELITE_BOOST / self.best_length
            for (ex, ey) in self.best_path:
                self.grid.deposit(ex, ey, elite_amount)

        self.grid.decay_all()
        self.tick_count += 1

    def get_state(self):
        """
        Serialize current state to plain JSON-safe structures.
        Sent to the frontend every tick (or every few ticks at high speed).
        """
        short_pct = None
        if self.gap_history:
            short_pct = round(100 * self.gap_history.count('short') / len(self.gap_history))

        return {
            "tick": self.tick_count,
            "nest": list(NEST_POS),
            "food": list(FOOD_POS),
            "obstacles": [list(o) for o in OBSTACLES],
            "pheromone": self.grid.pheromone,  # 2D list, JSON-safe as-is
            "ants": [
                {"x": a.x, "y": a.y, "hasFood": a.has_food}
                for a in self.ants
            ],
            "stats": {
                "tripsCompleted": self.trips_completed,
                "bestLength": self.best_length,
                "shortGapPercent": short_pct,
            },
        }
