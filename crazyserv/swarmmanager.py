from typing import Dict
import threading
from .drone import Drone
from .swarm import Swarm


class SwarmManager:
    """Class that handles swarms."""

    def __init__(self):
        self.swarms: Dict[str, Swarm] = {}
        self._lock = threading.Lock()

    def get_swarm(self, swarm_id: str) -> Swarm:
        """Gets the swarm with the given id.

        Arguments:
            swarm_id {str} -- The id for the swarm to get.

        Returns:
            Swarm -- The swarm with the given id, None if no such swarm exists.
        """

        if not swarm_id in self.swarms:
            return None
        return self.swarms.get(swarm_id)

    def add_drone(self, swarm_id: str, drone_id: int) -> Drone:
        """Adds a drone to the swarm. Creates the swarm if it does not exist yet.

        Arguments:
            swarm_id {str} -- The swarm id to add the drone to.
            drone_id {int} -- The drone id of the drone to add to the swarm.

        Returns:
            Drone -- The added drone or None if adding failed.
        """

        swarm = self._get_or_add_swarm(swarm_id)
        success = swarm.add_drone(drone_id)
        if success:
            return swarm.get_drone(drone_id)
        return None

    def remove_drone(self, swarm_id: str, drone_id: int) -> bool:
        """Removes a drone from a swarm.

        Arguments:
            swarm_id {str} -- The id of the swarm where the drone should be removed.
            drone_id {int} -- The id of the drone which should be removed from the swarm.

        Returns:
            bool -- True if the drone was removed, False otherwise.
        """

        swarm = self.get_swarm(swarm_id)
        if swarm is not None:
            return swarm.remove_drone(drone_id)
        return False

    def get_drone(self, swarm_id: str, drone_id: int) -> Drone:
        """Gets a specific drone from a specific swarm.

        Arguments:
            swarm_id {str} -- The id of the swarm to get the drone from.
            drone_id {int} -- The id of the drone to get from the swarm.

        Returns:
            Drone -- The drone if one exists, None otherwise.
        """

        swarm = self.get_swarm(swarm_id)
        if swarm is None:
            return None
        return swarm.get_drone(drone_id)

    def _get_or_add_swarm(self, swarm_id: str) -> Swarm:
        self._lock.acquire()
        if not swarm_id in self.swarms:
            self.swarms[swarm_id] = Swarm(swarm_id)
        self._lock.release()
        return self.swarms.get(swarm_id)
