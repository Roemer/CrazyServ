import random
import json
import numpy as np
from .obstacle import Obstacle


class Arena:

    def __init__(self, seed):
        self.rng_seed = seed
        self.arena_x_length = 4
        self.arena_y_length = 4
        self.fixed_z = 0.5
        self.obstacles = np.array([])

        random.seed(self.rng_seed)
        self._load_obstacles()

    def generate_coordinate_triplet(self):
        while(True):
            x_proposition = self.arena_x_length * random.random()
            y_proposition = self.arena_y_length * random.random()
            z_proposition = self.fixed_z

            if (self.position_is_valid(x_proposition, y_proposition, z_proposition)):
                return x_proposition, y_proposition, z_proposition

    # This simply tests if the coordinate lies in a no-fly zone
    def position_is_valid(self, x, y, z):
        for obstacle in self.obstacles:
            if obstacle.coordinate_is_blocked(x, y):
                return False

        return True

    def _load_obstacles(self):
        self.obstacles = np.array([
            Obstacle(left=1, right=2, upper=3, lower=2),
            Obstacle(left=3.4, right=2.5, upper=1.3, lower=1.0)
        ])
