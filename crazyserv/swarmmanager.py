from typing import Dict
import threading
from .drone import Drone
from .swarm import Swarm
from .arena import Arena


class SwarmManager:
    """Class that handles swarms."""

    def __init__(self):
        self.swarms: Dict[str, Swarm] = {}
        self.arenas = {}
        self._lock = threading.Lock()

    def register_swarm(self, swarm_id, arena_id):
        self._lock.acquire()
        try:
        if swarm_id in self.arenas: 
            return False
        self.arenas[swarm_id] = Arena(arena_id)
        self.swarms[swarm_id] = Swarm(swarm_id)
        self._lock.release()
        return True
        finally:
            self._lock.release()

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

    def get_arena(self, swarm_id: str) -> Swarm:
        if not swarm_id in self.arenas:
            return None
        return self.arenas[swarm_id]

    def add_drone(self, swarm_id: str, drone_id: str, radio_id: int, channel: int, address: str, data_rate: str) -> Drone:
        """Adds a drone to the swarm. Creates the swarm if it does not exist yet.

        Arguments:
            swarm_id {str} -- The swarm id to add the drone to.
            drone_id {str} -- The drone id of the drone to add to the swarm.

        Returns:
            Drone -- The added drone or None if adding failed.
        """

        swarm = self.get_swarm(swarm_id)
        arena = self.get_arena(swarm_id)
        success = swarm.add_drone(drone_id, arena, radio_id, channel, address, data_rate)
        if success:
            return swarm.get_drone(drone_id)
        return None

    def remove_drone(self, swarm_id: str, drone_id: str) -> bool:
        """Removes a drone from a swarm.

        Arguments:
            swarm_id {str} -- The id of the swarm where the drone should be removed.
            drone_id {str} -- The id of the drone which should be removed from the swarm.

        Returns:
            bool -- True if the drone was removed, False otherwise.
        """

        swarm = self.get_swarm(swarm_id)
        if swarm is not None:
            return swarm.remove_drone(drone_id)
        return False

    def get_drone(self, swarm_id: str, drone_id: str) -> Drone:
        """Gets a specific drone from a specific swarm.

        Arguments:
            swarm_id {str} -- The id of the swarm to get the drone from.
            drone_id {str} -- The id of the drone to get from the swarm.

        Returns:
            Drone -- The drone if one exists, None otherwise.
        """

        swarm = self.get_swarm(swarm_id)
        if swarm is None:
            return None
        return swarm.get_drone(drone_id)
