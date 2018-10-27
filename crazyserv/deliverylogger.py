import numpy as np

from .drone import Drone

class DeliveryLogger: 
    def __init__(self):
        self.log = {}
        self.count = 0
        self.sensitivity = 0.2

    def add_package(self, swarm_id, package):
        package_id = package['id']
        self.log[package_id] = package
        self.swarm_id = swarm_id

    def deliver_package(self, swarm_id, package_id, drone: Drone):
        if package_id not in self.log:
            return False

        package = self.log[package_id]
        if self.drone_is_in_landing_zone(drone, package['coordinates']):
            self.log.pop(package_id)
            self.count += 1
            return True

        return False

    def drone_is_in_landing_zone(self, drone: Drone, coordinates: []):
        status = drone.get_status()
        return np.sqrt((status['x'] - coordinates[0])**2 + (status['y'] - coordinates[1])**2) < self.sensitivity

    # TODO: thread-safe implementation of file operation
    def print_deliveries(self):
        log_file = open(self.swarm_id + "_results.txt", "w")
        log_file.write("Swarm " + self.swarm_id + " has " + str(self.count) + " deliveries")
        log_file.close()
        return True
