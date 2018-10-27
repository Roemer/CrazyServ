
class Arena:
    def __init__(self, arena_id: int,
                 min_x: float, max_x: float,
                 min_y: float, max_y: float,
                 min_z: float, max_z: float,
                 offset_x: float, offset_y: float, offset_z: float):

        self.arena_id = arena_id

        self.min_x: float = min_x
        self.max_x: float = max_x

        self.min_y: float = min_y
        self.max_y: float = max_y

        self.min_z: float = min_z
        self.max_z: float = max_z

        self.offset_x = offset_x
        self.offset_y = offset_y
        self.offset_z = offset_z

    def transform_x(self, x):
        return x + self.offset_x

    def transform_y(self, y):
        return y + self.offset_y

    def transform_z(self, z):
        return z + self.offset_z

    def transform_x_inverse(self, x):
        return x - self.offset_x

    def transform_y_inverse(self, y):
        return y - self.offset_y

    def transform_z_inverse(self, z):
        return z - self.offset_z
