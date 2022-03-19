import sys

import numpy as np
import pygame

from PlanningCore.billiard import Ball, Table
from PlanningCore.core.constants import State
from PlanningCore.core import constants as c
from PlanningCore.core.physics import ball_ball_collision, ball_cushion_collision, evolve_ball_motion, Force, cue_strike
from PlanningCore.core.plan import search_optimal_strike
from PlanningCore.core.utils import get_rel_velocity


def evolve(balls, dt):
    for ball in balls:
        rvw, state = evolve_ball_motion(
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


def simulate(table, dt=0.033):
    for t in np.diff(np.arange(0, 5, dt)):
        if np.all([ball.state == State.stationary for ball in table.balls]):
            break
        evolve(table.balls, t)
        table.snapshot(t)

        collisions = detect_collisions(table)
        for collision in collisions:
            resolve(collision, table)
            table.snapshot(t)


def get_demo_table():
    cue_ball = Ball(no=0, color='white', pos=(c.table_width / 2, 0.33), radius=c.ball_radius, is_cue=True)
    ball7 = Ball(no=7, color='blue', pos=(c.table_width/2 - c.table_width/5, 0.91), radius=c.ball_radius)
    ball3 = Ball(no=3, color='yellow', pos=(c.table_width/2 + c.table_width/6 + 0.2, 1.2), radius=c.ball_radius)
    ball9 = Ball(no=9, color='black', pos=(c.table_width / 2, 0.66), radius=c.ball_radius)
    balls = [cue_ball, ball3, ball7, ball9]
    table = Table(width=c.table_width, height=c.table_height, balls=balls, pockets=None)
    return table


def shot(table, v_cue, phi, theta, a, b):
    v, w = cue_strike(v_cue, phi, theta, a, b)
    rvw = table.balls[0].rvw
    rvw[1] = v
    rvw[2] = w
    state = State.rolling if np.abs(np.sum(get_rel_velocity(rvw))) <= 1e-10 else State.sliding
    table.balls[0].set_rvw(rvw)
    table.balls[0].set_state(state)


def animate(logs, flip=False):
    from PlanningCore.billiard.visualize import COLOR_MAP

    cloth_color = (202, 222, 235)
    scale = 800 / max([c.table_width, c.table_height])
    screen_width = scale * c.table_height if flip else c.table_width
    screen_height = scale * c.table_width if flip else c.table_height
    radius = c.ball_radius * scale

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.HWSURFACE | pygame.DOUBLEBUF)
    clock = pygame.time.Clock()

    def draw_table():
        screen.fill(cloth_color)

    def draw_balls(balls):
        for ball in balls:
            rvw = ball['rvw']
            x = rvw[0][0] * scale
            y = rvw[0][1] * scale
            pygame.draw.ellipse(
                surface=screen,
                color=COLOR_MAP[ball['color']],
                rect=(y - radius, x - radius, radius * 2, radius * 2),
            )

    while True:
        for log in logs:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            draw_table()
            draw_balls(log['balls'])
            pygame.display.update()
            clock.tick(60)


if __name__ == '__main__':
    t = get_demo_table()
    shot(
        table=t,
        v_cue=0.5,
        phi=96,
        theta=0,
        a=0,
        b=0,
    )
    simulate(t, dt=0.02)
    animate(t.log, True)