from itertools import combinations

import numpy as np

from PlanningCore.core.constants import State
from PlanningCore.core.physics import (
    ball_ball_collision,
    ball_cushion_collision,
    cue_strike,
    evolve_ball_motion,
    get_ball_ball_collision_time,
    get_ball_cushion_collision_time,
    get_roll_time,
    get_spin_time,
    get_slide_time,
)
from PlanningCore.core.utils import get_rel_velocity


def evolve(pockets, balls, dt):
    for ball in balls:
        rvw, state = evolve_ball_motion(
            pockets=pockets,
            state=ball.state,
            rvw=ball.rvw,
            t=dt,
        )
        ball.set_rvw(rvw)
        ball.set_state(state)


def resolve(collision, table):
    if collision['type'] == 'ball_ball':
        ball_id1, ball_id2 = collision['agents']

        rvw1 = table.balls[ball_id1].rvw
        rvw2 = table.balls[ball_id2].rvw

        rvw1, rvw2 = ball_ball_collision(rvw1, rvw2)
        s1, s2 = State.sliding, State.sliding

        table.balls[ball_id1].set_rvw(rvw1)
        table.balls[ball_id1].set_state(s1)
        table.balls[ball_id2].set_rvw(rvw2)
        table.balls[ball_id2].set_state(s2)

    elif collision['type'] == 'ball_cushion':
        ball_id, cushion_id = collision['agents']

        rvw = table.balls[ball_id].rvw
        normal = table.cushions[cushion_id]['normal']

        rvw = ball_cushion_collision(rvw, normal)
        s = State.sliding

        table.balls[ball_id].set_rvw(rvw)
        table.balls[ball_id].set_state(s)


def detect_collisions(table):
    collisions = []

    for i, ball1 in enumerate(table.balls):
        for j, ball2 in enumerate(table.balls):
            if i >= j:
                continue
            if ball1.state == State.stationary and ball2.state == State.stationary:
                continue

            if np.linalg.norm(ball1.rvw[0] - ball2.rvw[0]) <= (ball1.radius + ball2.radius):
                collisions.append({
                    'type': 'ball_ball',
                    'agents': (i, j),
                })

    for i, ball in enumerate(table.balls):
        ball_x, ball_y = ball.pos
        if ball_x <= table.left + ball.radius:
            collisions.append({
                'type': 'ball_cushion',
                'agents': (i, 'L'),
            })
        elif ball_x >= table.right - ball.radius:
            collisions.append({
                'type': 'ball_cushion',
                'agents': (i, 'R'),
            })
        elif ball_y <= table.bottom + ball.radius:
            collisions.append({
                'type': 'ball_cushion',
                'agents': (i, 'B'),
            })
        elif ball_y >= table.top - ball.radius:
            collisions.append({
                'type': 'ball_cushion',
                'agents': (i, 'T'),
            })
    return collisions


def get_min_motion_event_time(balls):
    t_min = np.inf
    ball_id = None
    motion_type = None

    for i, ball in enumerate(balls):
        if ball.state == State.rolling:
            t = get_roll_time(ball.rvw)
            tau_spin = get_spin_time(ball.rvw)
            event_type = 'rolling_spinning' if tau_spin > t else 'rolling_stationary'
        elif ball.state == State.sliding:
            t = get_slide_time(ball.rvw)
            event_type = 'sliding_rolling'
        elif ball.state == State.spinning:
            t = get_spin_time(ball.rvw)
            event_type = 'spinning_stationary'
        else:
            continue

        if t < t_min:
            t_min = t
            ball_id = i
            motion_type = event_type

    return t_min, (ball_id,), motion_type


def get_min_ball_ball_event_time(balls):
    t_min = np.inf
    ball_ids = (None, None)

    for (i, ball1), (j, ball2) in combinations(enumerate(balls), 2):
        if ball1.state == State.pocketed or ball2.state == State.pocketed:
            continue

        if ball1.state == State.stationary and ball2.state == State.stationary:
            continue

        t = get_ball_ball_collision_time(
            rvw1=ball1.rvw,
            rvw2=ball2.rvw,
            s1=ball1.state,
            s2=ball2.state,
        )

        if t < t_min:
            ball_ids = (i, j)
            t_min = t

    return t_min, ball_ids


def get_min_ball_cushion_event_time(balls, cushions):
    """Returns minimum time until next ball-rail collision"""

    t_min = np.inf
    agents = (None, None)

    for ball_id, ball in enumerate(balls):
        if ball.state == State.stationary or ball.state == State.pocketed:
            continue

        for cushion_id, cushion in cushions.items():
            t = get_ball_cushion_collision_time(
                rvw=ball.rvw,
                s=ball.state,
                lx=cushion['lx'],
                ly=cushion['ly'],
                l0=cushion['l0'],
            )

            if t < t_min:
                agents = (ball_id, cushion_id)
                t_min = t

    return t_min, agents


def get_next_event(table):
    t_min = np.inf
    agents = tuple()
    event_type = None

    t, ids, e = get_min_motion_event_time(table.balls)
    if t < t_min:
        t_min = t
        event_type = e
        agents = ids

    t, ids = get_min_ball_ball_event_time(table.balls)
    if t < t_min:
        t_min = t
        event_type = 'ball_ball'
        agents = ids

    t, ids = get_min_ball_cushion_event_time(table.balls, table.cushions)
    if t < t_min:
        t_min = t
        event_type = 'ball_cushion'
        agents = ids
    return Event(event_type=event_type, event_time=t_min, agents=agents)


def simulate(table, dt=0.033, log=False, no_ball_cushion=False, return_once_pocket=False):
    while True:
        if return_once_pocket:
            for ball in table.balls:
                if ball.state == State.pocketed:
                    return True
        if np.all([(ball.state == State.stationary or ball.state == State.pocketed)
                   for ball in table.balls]):
            break
        evolve(table.pockets, table.balls, dt)
        if log:
            table.snapshot(dt)

        collisions = detect_collisions(table)
        for collision in collisions:
            if no_ball_cushion and collision['type'] == 'ball_cushion':
                return False
            resolve(collision, table)
            if log:
                table.snapshot(dt)
    return True


def simulate_event_based(table, log=False, return_once_pocket=False):
    event = Event()
    while event.event_time < np.inf:
        event = get_next_event(table)
        if return_once_pocket:
            for ball in table.balls:
                if ball.state == State.pocketed:
                    return True
        if np.all([(ball.state == State.stationary or ball.state == State.pocketed)
                   for ball in table.balls]):
            break
        evolve(table.pockets, table.balls, dt=event.event_time)
        resolve(event.as_dict(), table)
        if log:
            table.snapshot(event.event_time)
    return True


def shot(table, v_cue, phi, ball_index=0, theta=0, a=0, b=0):
    v, w = cue_strike(v_cue, phi, theta, a, b)
    rvw = table.balls[ball_index].rvw
    rvw[1] = v
    rvw[2] = w
    state = State.rolling if np.abs(np.sum(get_rel_velocity(rvw))) <= 1e-10 else State.sliding
    table.balls[ball_index].set_rvw(rvw)
    table.balls[ball_index].set_state(state)


class Event(object):

    def __init__(self, event_type=None, event_time=0, agents=None):
        self.event_type = event_type
        self.event_time = event_time
        self.agents = agents

    def as_dict(self):
        return {
            'type': self.event_type,
            'time': self.event_time,
            'agents': self.agents,
        }