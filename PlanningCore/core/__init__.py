class Force(object):
    def __init__(self, magnitude, direction):
        self.magnitude = magnitude
        self.direction = direction

    def __repr__(self):
        return f'Force(magnitude={self.magnitude}, direction={self.direction})'