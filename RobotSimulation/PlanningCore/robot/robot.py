class Robot(object):
    def __init__(self, pos):
        self.pos = pos

    def __repr__(self):
        return f'Robot(pos={self.pos})'