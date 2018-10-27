from .arena import Arena


class ArenaManager:
    def __init__(self,):
        self.arenas = {}
        self.arenas[0] = Arena(0, -2, 2, -2, 2, 0, 1.2, offset_x=+2, offset_y=+2, offset_z=0)
        self.arenas[1] = Arena(1, 2, 6, -2, 2, 0, 1.2, offset_x=-2, offset_y=+2, offset_z=0)
        self.arenas[2] = Arena(2, 2, 6, -6, -2, 0, 1.2, offset_x=-2, offset_y=+6, offset_z=0)
