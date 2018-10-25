from typing import Dict
import threading
from .drone import Drone


class Swarm:
    """Class that handles a swarm."""

    def __init__(self, swarm_id: str):
        self.id: str = swarm_id
        self.drones: Dict[int, Drone] = {}
        self._lock = threading.Lock()

    def add_drone(self, drone_id: int) -> bool:
        """Adds a new drone with the given id to the swarm.

        Arguments:
            drone_id {int} -- THe id of the drone that should be added.

        Returns:
            bool -- True if the drone was added successfully, False otherwise.
        """

        # Try to create and connect to the drone
        drone = Drone(drone_id)
        drone.connect(synchronous=True)
        # Check if the connection to the drone was successfull
        if (not drone.is_connected):
            # Connection failed
            return False
        # Connection successfull, configure the drone
        drone.enable_high_level_commander()
        drone.reset_estimator()
        # Remove a possible existing drone from the swarm
        self.remove_drone(drone.id)
        # Add the new drone to the swarm
        self.drones[drone.id] = drone
        # Add a callback when the drone is lost
        drone.drone_lost.add_callback(self._drone_connection_lost)
        return True

    def remove_drone(self, drone_id: int) -> bool:
        """Tries to disconnect and remove the drone with the given id from the swarm.

        Arguments:
            drone_id {int} -- The id of the drone that should be removed.

        Returns:
            bool -- True if the drone was found and removed, false if the drone was not found.
        """

        if drone_id in self.drones:
            drone = self.drones.get(drone_id)
            self.drones.pop(drone_id)
            # Try to disconnect the drone
            try:
                drone.drone_lost.remove_callback(self._drone_connection_lost)
                drone.disconnect()
            except:
                pass
            return True
        return False

    def get_drone(self, drone_id: int) -> Drone:
        """Gets the drone with the given id from the swarm.

        Arguments:
            drone_id {int} -- The id of the drone to get.

        Returns:
            Drone -- The drone object or None if no drone with the given id exists.
        """

        if drone_id in self.drones:
            return self.drones.get(drone_id)
        return None

    def _drone_connection_lost(self, drone: Drone):
        self.remove_drone(drone.id)
