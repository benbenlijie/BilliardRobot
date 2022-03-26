from copy import deepcopy
from itertools import product
import numpy as np

import PlanningCore.core
from PlanningCore.core import State
from PlanningCore.core import constants, coordinate_transformation


class Ball(object):
    def __init__(self, no, color, pos=(0, 0), radius=10, is_cue=False):
        self.no = no
        self.color = color
        self.pos = pos
        self.radius = radius
        self.is_cue = is_cue
        self.velocity = (0, 0, 0)
        self.angular_velocity = (0, 0, 0)
        self.force_angle = 0
        self.state = State.stationary

    def __repr__(self):
        return f'Ball(no={self.no}, color={self.color}, pos={self.pos}, cue={self.is_cue})'

    def set_state(self, state):
        self.state = state

    def set_pos(self, pos):
        self.pos = pos[:2]

    def set_velocity(self, velocity):
        self.velocity = velocity

    def set_angular_velocity(self, angular_velocity):
        self.angular_velocity = angular_velocity

    def set_rvw(self, rvw):
        r, v, w = rvw
        self.set_pos(r)
        self.set_velocity(v)
        self.set_angular_velocity(w)

    @property
    def rvw(self):
        return np.array([[*self.pos, 0], self.velocity, self.angular_velocity])

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
        self.pos = target_pos
        print(f'{self} moving to {self.pos}')


class Pocket(object):
    def __init__(self, no, pos, radius=15):
        self.no = no
        self.radius = radius
        self.pos = pos
        self.balls = []

    def __repr__(self):
        return f'Pocket(no={self.no}, balls={self.balls})'


class Table(object):
    def __init__(self, width, height, balls, pockets):
        self.width = width
        self.height = height
        self.balls = balls
        self.init_balls = deepcopy(self.balls)
        self.pockets = pockets
        self.left = 0
        self.right = self.width
        self.bottom = 0
        self.top = self.height
        self.normal = {
            'L': np.array((1, 0)),
            'R': np.array((1, 0)),
            'B': np.array((0, 1)),
            'T': np.array((0, 1)),
        }

        self.time = 0
        self.n = 0
        self.log = []
        self.snapshot(0)
        print(f'{self} initialized')

    def __repr__(self):
        return (
            f'Table(width={self.width}, height={self.height}'
            f'balls={self.balls}, pockets={self.pockets})'
        )

    def reset_balls(self):
        self.balls = deepcopy(self.init_balls)
        self.log = []
        self.snapshot(0)

    def snapshot(self, dt):
        self.n += 1
        self.time += dt
        self.log.append({
            'time': self.time,
            'index': self.n,
            'balls': [{'state': ball.state, 'rvw': ball.rvw, 'color': ball.color} for ball in self.balls],
        })


def init_table(cue_ball_pos, balls_pos):
    cue_ball = Ball(no=0, color='white', pos=coordinate_transformation(cue_ball_pos), radius=constants.ball_radius, is_cue=True)
    balls = [Ball(no=i+1, color='yellow', pos=coordinate_transformation(pos), radius=constants.ball_radius) for i,pos in enumerate(balls_pos)]
    balls.insert(0, cue_ball)
    pockets = [Pocket(no=i, pos=(x, y), radius=constants.pocket_radius)
               for i, (x, y) in enumerate(product((0, constants.table_width), (0, constants.table_height/2, constants.table_height)))]
    table = Table(width=constants.table_width, height=constants.table_height, balls=balls, pockets=pockets)
    return table