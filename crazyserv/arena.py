
class Arena:
    def __init__(self):
        self.min_x: float = 0
        self.max_x: float = 2

        self.min_y: float = 0
        self.max_y: float = 2

        self.min_z: float = -0.2
        self.max_z: float = 2

    def get_min_z(self):
        return self.min_z
