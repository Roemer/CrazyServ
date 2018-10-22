class Obstacle:
    def __init__(self, left, right, upper, lower):
        self.left_boundary = left
        self.right_boundary = right
        self.upper_boundary = upper
        self.lower_boundary = lower

    def coordinate_is_blocked(self, x, y):
        if x < self.left_boundary:
            return False
        if x > self.right_boundary: 
            return False
        if y < self.lower_boundary:
            return False
        if y > self.upper_boundary:
            return False
        return True