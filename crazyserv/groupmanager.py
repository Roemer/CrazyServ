import threading
from .group import Group


class GroupManager:
    """ Class that handles the list of groups. """

    def __init__(self):
        self.groups = []
        self.lock = threading.Lock()

    def getGroup(self, groupId):
        """ Returns the group with the given id or None if such a group does not exist. """
        self.lock.acquire()
        try:
            for group in self.groups:
                if group.id == groupId:
                    # Found it, return it
                    return group
            return None
        finally:
            self.lock.release()

    def getOrAddGroup(self, groupId):
        """ Gets or creates the group with the given id. """
        self.lock.acquire()
        try:
            # Search for the group with the given id
            for group in self.groups:
                if group.id == groupId:
                    # Found it, return it
                    return group
            # Create and add it
            group = Group(groupId)
            self.groups.append(group)
            return group
        finally:
            self.lock.release()
