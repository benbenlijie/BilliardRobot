from PlanningCore.core.constants import State


class Ball(object):
    def __init__(self, no, color, pos=(0, 0), radius=10, is_cue=False):
        self.no = no
        self.color = color
        self.x, self.y = pos
        self.radius = radius
        self.is_cue = is_cue
        self.velocity = 0
        self.angular_velocity = 0
        self.force_angle = 0
        self._state = State.stationary

    def __repr__(self):
        return f'Ball(no={self.no}, color={self.color}, pos={self.x, self.y}, cue={self.is_cue})'

    @property
    def state(self):
        return self._state

    def set_state(self, state):
        self._state = state

    def apply_force(self, force):
        """
        受到力之后得到速度和角度
        """
        self.velocity = force.magnitude
        self.force_angle = force.direction
        print(f'{self} is subjected to force {force}')

    def move(self, target_pos):
        """
        这里的x和y不是球心，是这个圆的外界正方形的左下角
        :return:
        """
        self.x, self.y = target_pos
        print(f'{self} moving to {self.x, self.y}')


class Pocket(object):
    def __init__(self, no, x, y, radius=15):
        self.no = no
        self.radius = radius
        self.x = x
        self.y = y
        self.balls = []

    def __repr__(self):
        return f'Pocket(no={self.no}, balls={self.balls})'


class Table(object):
    def __init__(self, width, height, margin, friction, balls, pockets):
        self.width = width
        self.height = height
        self.margin = margin
        self.friction = friction
        self.balls = balls
        self.pockets = pockets
        print(f'{self} initialized')

    def __repr__(self):
        return (
            f'Table(width={self.width}, height={self.height}, friction={self.friction}, '
            f'balls={self.balls}, pockets={self.pockets})'
        )