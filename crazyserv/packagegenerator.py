import random
import numpy as np
from .arena import Arena
from .deliverylogger import DeliveryLogger
from .drone import Drone


class PackageGenerator:
    def __init__(self):
        self.coordinate_pool = self.define_coordinate_pool()
        self.pool_size = self.coordinate_pool.shape[0]
        self.package_weight = 3
        self.rng = {}
        self.delivery_loggers = {}

    def define_coordinate_pool(self):
        arena = Arena(0)
        z = arena.min_z
        return np.array([
            [2.6, 0.6, z],
            [2.4, 3.4, z],
            [0.6, 2.2, z],
            [1.4, 3.2, z],
            [1., 1.6, z],
            [3.6, 0.6, z],
            [3.2, 3.2, z],
            [3.4, 1.4, z]
        ])

    def initialize_swarm(self, swarm_id, seed):
        self.rng[swarm_id] = random.Random()
        self.rng[swarm_id].seed(seed)
        self.delivery_loggers[swarm_id] = DeliveryLogger()
        return True

    def generate_number(self, swarm_id, lower_limit, upper_limit):
        return self.rng[swarm_id].randint(lower_limit, upper_limit)

    def generate_hash(self, swarm_id):
        return self.rng[swarm_id].getrandbits(128)

    def get_package(self, swarm_id):
        rand = self.generate_number(swarm_id, 0, self.pool_size - 1)
        weight = self.generate_number(swarm_id, 1, self.package_weight)
        id = self.generate_hash(swarm_id)

        package = {'id': id, 'coordinates': self.coordinate_pool[rand].tolist(), 'weight': weight}
        
        self.delivery_loggers[swarm_id].add_package(swarm_id, package)
        return package

    def deliver_package(self, swarm_id, package_id, drone: Drone):
        success = self.delivery_loggers[swarm_id].deliver_package(swarm_id, package_id, drone)
        return success

    def print_deliveries(self, swarm_id):
        success = self.delivery_loggers[swarm_id].print_deliveries()
        return success
