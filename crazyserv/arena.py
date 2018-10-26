
class Arena:
    def __init__(self, arena_id):
        self.min_x: float = 0
        self.max_x: float = 2

        self.min_y: float = 0
        self.max_y: float = 2

        self.min_z: float = -0.2
        self.max_z: float = 2

        self.arena_id = arena_id
        self.arena_offsets = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    def transform_x(self, x):
        return x + self.arena_offsets[self.arena_id][0]

    def transform_y(self, y):
        return y + self.arena_offsets[self.arena_id][1]

    def transform_z(self, z):
        return z + self.arena_offsets[self.arena_id][2]
