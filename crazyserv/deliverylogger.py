import numpy as np

from .drone import Drone


class DeliveryLogger:
    def __init__(self):
        self.log = {}
        self.count = 0
        self.count_weight_exceeded = 0
        self.max_weight = 3
        self.drone_load = {}
        self.sensitivity = 0.25
        self.sensitivity_z = 0.2

    def add_package(self, swarm_id, package):
        package_id = package['id']
        self.log[package_id] = package
        self.swarm_id = swarm_id

    def pickup(self, swarm_id, package_id, drone: Drone):
        if package_id not in self.log:
            return False
        package = self.log[package_id]
        if package['picked']:
            return False
        if self.drone_is_in_landing_zone(drone, [2.2, 1.6]):
            new_drone_load = self.drone_load.get(drone.id, 0) + package['weight']
            if new_drone_load > self.max_weight:
                self.count_weight_exceeded += 1
                return False
            package['drone'] = drone.id
            package['picked'] = True
            self.drone_load[drone.id] = new_drone_load
            return True
        return False

    def deliver(self, swarm_id, package_id, drone: Drone):
        if package_id not in self.log:
            return False
        package = self.log[package_id]
        if package['drone'] is None or package['drone'] != drone.id:
            return False
        if self.drone_is_in_landing_zone(drone, package['coordinates']):
            self.log.pop(package_id)
            self.count += 1
            self.drone_load[drone.id] -= package['weight']
            return True
        return False

    def drone_is_in_landing_zone(self, drone: Drone, coordinates: []):
        status = drone.get_status()
        return np.sqrt((status['x'] - coordinates[0])**2 + (status['y'] - coordinates[1])**2) < self.sensitivity and status['z'] < self.sensitivity_z

    def log_is_full(self, swarm_id):
        return len(self.log) >= 20

    # TODO: thread-safe implementation of file operation
    def print_deliveries(self):
        log_file = open(self.swarm_id + "_results.txt", "w")
        log_file.write("Swarm " + self.swarm_id + " has " + str(self.count) + " deliveries and " + str(len(self.log)) +
                       " still pending and " + str(self.count_weight_exceeded) + " weight exceeds on a drone.")
        log_file.close()
        return True
