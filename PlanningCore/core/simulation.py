import numpy as np

from PlanningCore.core.physics import (
    ball_ball_collision,
    ball_cushion_collision,
    cue_strike,
    evolve_ball_motion,
)
from PlanningCore.core.utils import get_rel_velocity
from PlanningCore.core.constants import State


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
        normal = table.normal[cushion_id]

        rvw = ball_cushion_collision(rvw, normal)
        s = State.sliding

        table.balls[ball_id].set_rvw(rvw)
        table.balls[ball_id].set_state(s)


def simulate(table, dt=0.033, log=False):
    while True:
        if np.all([(ball.state == State.stationary or ball.state == State.pocketed) for ball in table.balls]):
            break
        evolve(table.pockets, table.balls, dt)
        if log:
            table.snapshot(dt)

        collisions = detect_collisions(table)
        for collision in collisions:
            if collision['type'] == 'ball_cushion':
                return False
            resolve(collision, table)
            if log:
                table.snapshot(dt)
    return True


def shot(table, v_cue, phi, theta=0, a=0, b=0):
    v, w = cue_strike(v_cue, phi, theta, a, b)
    rvw = table.balls[0].rvw
    rvw[1] = v
    rvw[2] = w
    state = State.rolling if np.abs(np.sum(get_rel_velocity(rvw))) <= 1e-10 else State.sliding
    table.balls[0].set_rvw(rvw)
    table.balls[0].set_state(state)