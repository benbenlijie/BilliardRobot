from copy import deepcopy
from itertools import product

import numpy as np

from PlanningCore.core import (
    coordinate_transformation,
    constants as c,
    get_common_tangent_angles,
    get_line_formula,
    State,
)


def init_table(cue_ball_pos, balls_pos):
    cue_ball = Ball(
        no=0,
        color='white',
        pos=coordinate_transformation(cue_ball_pos),
        radius=c.ball_radius, is_cue=True,
    )
    balls = [Ball(
        no=i + 1,
        color='yellow',
        pos=coordinate_transformation(pos),
        radius=c.ball_radius,
    ) for i, pos in enumerate(balls_pos)]
    balls.insert(0, cue_ball)
    pockets = [Pocket(no=i, pos=(x, y), radius=c.pocket_radius)
               for i, (x, y) in enumerate(product((0, c.table_width), (0, c.table_height / 2, c.table_height)))]
    table = Table(width=c.table_width, height=c.table_height, balls=balls, pockets=pockets)
    return table


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
        return (f'Ball(no={self.no}, pos=(x: {self.pos[0]:.2f}, y: {self.pos[1]:.2f}), '
                f'state={State.all[self.state]}{", cue_ball" if self.is_cue else ""})')

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


class Pocket(object):
    def __init__(self, no, pos, radius=15):
        self.no = no
        self.radius = radius
        self.pos = pos
        self.balls = []

    def __repr__(self):
        return f'Pocket(no={self.no}, pos=(x: {self.pos[0]:.2f}, y: {self.pos[1]:.2f}))'


class Table(object):
    def __init__(self, width, height, balls, pockets):
        self.width = width
        self.height = height
        self.balls = balls
        self.pockets = pockets
        self.sort_balls()
        self.init_balls = deepcopy(self.balls)
        self.left = 0
        self.right = self.width
        self.bottom = 0
        self.top = self.height
        self.cushions = {
            'L': {'normal': np.array((1, 0)), 'lx': 1, 'ly': 0, 'l0': -self.left},
            'R': {'normal': np.array((1, 0)), 'lx': 1, 'ly': 0, 'l0': -self.right},
            'B': {'normal': np.array((0, 1)), 'lx': 0, 'ly': 1, 'l0': -self.bottom},
            'T': {'normal': np.array((0, 1)), 'lx': 0, 'ly': 1, 'l0': -self.top},
        }

        self.time = 0
        self.n = 0
        self.log = []
        self.snapshot(0)
        print(f'{self} initialized')

    def __repr__(self):
        balls_str = '\n\t'.join(str(ball) for ball in self.balls)
        pockets_str = '\n\t'.join(str(pocket) for pocket in self.pockets)
        return (
            f'Table(width={self.width}, height={self.height}\n'
            f'balls=\n\t{balls_str}\npockets=\n\t{pockets_str}\n)'
        )

    def reset_balls(self):
        self.balls = deepcopy(self.init_balls)
        self.log = []
        self.n = 0
        self.time = 0
        self.snapshot(0)

    def snapshot(self, dt):
        self.n += 1
        self.time += dt
        self.log.append({
            'time': self.time,
            'index': self.n,
            'balls': [{'state': ball.state, 'rvw': ball.rvw, 'color': ball.color} for ball in self.balls],
        })

    def sort_balls(self):
        new_balls = [self.balls[0]]
        ball_value = {
            i: self.get_ball_value(ball, i)
            for i, ball in enumerate(self.balls[1:], 1)
        }
        ball_value = dict(sorted(ball_value.items(), key=lambda x: x[1], reverse=True))
        for i in ball_value.keys():
            new_balls.append(self.balls[i])
        self.balls = new_balls

    def get_ball_value(self, ball, index):
        value = 0
        angle1, angle2 = get_common_tangent_angles(self.balls[0], ball)
        for i, other_ball in enumerate(self.balls[1:], 1):
            if i == index:
                continue
            # Other ball between two lines.
            if self.is_between(angle1, angle2, other_ball.pos):
                value -= 5
        # Pocket between two lines.
        for pocket in self.pockets:
            if self.is_between(angle1, angle2, pocket.pos):
                value += 1
        return value

    def is_between(self, angle1, angle2, point):
        angle1 %= 360
        angle2 %= 360
        angle1, angle2 = sorted([angle1, angle2])
        line1 = get_line_formula(angle1, self.balls[0].pos)
        line2 = get_line_formula(angle2, self.balls[0].pos)
        y1 = line1(point[0])
        y2 = line2(point[0])
        y = point[1]
        if 180 < angle1 < 270 < angle2 < 360:
            return y <= y1 and y <= y2
        elif 0 < angle1 < 90 < angle2 < 180:
            return y >= y1 and y >= y2
        elif (
            (270 < angle1 < 360 and 270 < angle2 < 360)
            or (0 < angle1 < 90 and 0 < angle2 < 90)
        ):
            return y1 <= y <= y2
        else:
            return y2 <= y <= y1