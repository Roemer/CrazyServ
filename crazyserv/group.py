class Group:
    """ Class that handles a group. """

    def __init__(self, id):
        self.id = id
        self.drones = []

    def addDrone(self, drone):
        self.drones.append(drone)

    def removeDrone(self, drone):
        self.drones.remove(drone)
