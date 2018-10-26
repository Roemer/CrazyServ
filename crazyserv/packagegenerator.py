import random
import numpy as np
from crazyserv import Arena


class PackageGenerator:
    def __init__(self):
        self.coordinate_pool = self.define_coordinate_pool()
        self.pool_size = self.coordinate_pool.shape[0]
        self.package_weight = 3
        self.rng = {}

    def define_coordinate_pool(self):
        arena = Arena(0)
        z = arena.min_z
        return np.array([[1, 1, z], [2, 2, z], [2, 3, z], [1, 1.2, z]])

    def initialize_swarm(self, swarm_id, seed):
        self.rng[swarm_id] = random.Random()
        self.rng[swarm_id].seed(seed)
        return True

    def generate_number(self, swarm_id, lower_limit, upper_limit):
        if (swarm_id in self.rng):
            return self.rng[swarm_id].randint(lower_limit, upper_limit)

    def get_package(self, swarm_id):
        rand = self.generate_number(swarm_id, 0, self.pool_size - 1)
        weight = self.generate_number(swarm_id, 1, self.package_weight)
        return {'coordinates': self.coordinate_pool[rand].tolist(), 'weight': weight}
