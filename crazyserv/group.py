class Group:
    """Class that handles a group."""

    def __init__(self, id):
        self.id = id
        self.drones = []

    def add_drone(self, drone):
        self.drones.append(drone)

    def remove_drone(self, drone):
        self.drones.remove(drone)
