import threading
from .group import Group


class GroupManager:
    """Class that handles the list of groups."""

    def __init__(self):
        self.groups = []
        self._lock = threading.Lock()

    def get_group(self, group_id):
        """Returns the group with the given id or None if such a group does not exist."""
        self._lock.acquire()
        try:
            for group in self.groups:
                if group.id == group_id:
                    # Found it, return it
                    return group
            return None
        finally:
            self._lock.release()

    def get_or_add_group(self, group_id):
        """Gets or creates the group with the given id."""
        self._lock.acquire()
        try:
            # Search for the group with the given id
            for group in self.groups:
                if group.id == group_id:
                    # Found it, return it
                    return group
            # Create and add it
            group = Group(group_id)
            self.groups.append(group)
            return group
        finally:
            self._lock.release()

    def get_drone(self, group_id, drone_id):
        filteredGroups = [group for group in self.groups if group.id == group_id]

        if len(filteredGroups) == 0:
            return

        group = filteredGroups[0]

        filtered_drones = [drone for drone in group.drones if drone.id == drone_id]

        if len(filtered_drones) == 0:
            return

        return filtered_drones[0]
