import sys

import numpy as np
import pygame

from PlanningCore.billiard import Ball, Table, Pocket
from PlanningCore.core.constants import *
from PlanningCore.core.physics import *
from PlanningCore.core.planning import *
from PlanningCore.core.simulation import *
from PlanningCore.core.utils import *
from PlanningCore.core import constants as c


def get_demo_table():
    cue_ball = Ball(no=0, color='white', pos=(c.table_width / 2, 0.33), radius=c.ball_radius, is_cue=True)
    ball7 = Ball(no=7, color='blue', pos=(c.table_width/2 - c.table_width/5, 0.91), radius=c.ball_radius)
    ball3 = Ball(no=3, color='yellow', pos=(c.table_width/2 + c.table_width/6 + 0.2, 2.2), radius=c.ball_radius)
    ball9 = Ball(no=9, color='black', pos=(c.table_width / 2 - 1, 3.66), radius=c.ball_radius)
    balls = [cue_ball, ball3, ball9]
    pocket1 = Pocket(no=1, pos=(0, 0), radius=c.pocket_radius)
    pocket2 = Pocket(no=2, pos=(c.table_width, 0), radius=c.pocket_radius)
    pocket3 = Pocket(no=3, pos=(0, c.table_height / 2), radius=c.pocket_radius)
    pocket4 = Pocket(no=4, pos=(c.table_width, c.table_height / 2), radius=c.pocket_radius)
    pocket5 = Pocket(no=5, pos=(0, c.table_height), radius=c.pocket_radius)
    pocket6 = Pocket(no=6, pos=(c.table_width, c.table_height), radius=c.pocket_radius)
    pockets = [pocket1, pocket2, pocket3, pocket4, pocket5, pocket6]
    table = Table(width=c.table_width, height=c.table_height, balls=balls, pockets=pockets)
    return table


def animate(pockets, logs, flip=False):
    from PlanningCore.billiard.visualize import COLOR_MAP

    cloth_color = (202, 222, 235)
    scale = 800 / max([c.table_width, c.table_height])
    screen_width = scale * (c.table_height if flip else c.table_width)
    screen_height = scale * (c.table_width if flip else c.table_height)
    radius = c.ball_radius * scale
    pocket_radius = c.pocket_radius * scale

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.HWSURFACE | pygame.DOUBLEBUF)
    clock = pygame.time.Clock()

    def draw_table():
        screen.fill(cloth_color)

    def draw_balls(balls):
        for ball in balls:
            rvw = ball['rvw']
            x = scale * (rvw[0][0] if flip else rvw[0][1])
            y = scale * (rvw[0][1] if flip else rvw[0][0])
            pygame.draw.ellipse(
                surface=screen,
                color=COLOR_MAP[ball['color']] if ball['state'] != State.pocketed else COLOR_MAP['green'],
                rect=(y - radius, x - radius, radius * 2, radius * 2),
            )

    def draw_pockets(pockets):
        for pocket in pockets:
            x = scale * (pocket.pos[0] if flip else pocket.pos[1])
            y = scale * (pocket.pos[1] if flip else pocket.pos[0])
            pygame.draw.ellipse(
                surface=screen,
                color=COLOR_MAP['black'],
                rect=(y - pocket_radius, x - pocket_radius, pocket_radius * 2, pocket_radius * 2),
            )

    while True:
        for log in logs:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            draw_table()
            draw_balls(log['balls'])
            draw_pockets(pockets)
            pygame.display.update()
            clock.tick(60)


if __name__ == '__main__':
    t = get_demo_table()
    angles = search_optimal_strike(table=t, dt=0.02, dang=0.5)
    print(angles)
    shot(
        table=t,
        v_cue=1,
        phi=angles[-1][1],
        theta=0,
        a=0,
        b=0,
    )
    simulate(t, dt=0.02)
    animate(t.pockets, t.log, False)