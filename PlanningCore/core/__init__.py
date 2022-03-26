from PlanningCore.core.constants import *
from PlanningCore.core.physics import *
from PlanningCore.core.planning import *
from PlanningCore.core.simulation import *
from PlanningCore.core.utils import *


def get_demo_table():
    from itertools import product

    from PlanningCore.billiard import Ball, Table, Pocket
    cue_ball = Ball(no=0, color='white', pos=(table_width / 2, 0.33), radius=ball_radius, is_cue=True)
    ball7 = Ball(no=7, color='blue', pos=(table_width/2 - table_width/5, 0.91), radius=ball_radius)
    ball3 = Ball(no=3, color='yellow', pos=(table_width/2 + table_width/6 + 0.2, 2.2), radius=ball_radius)
    ball9 = Ball(no=9, color='black', pos=(table_width / 2 - 1, 3.66), radius=ball_radius)
    balls = [cue_ball, ball3, ball9]
    pockets = [Pocket(no=i, pos=(x, y), radius=pocket_radius)
               for i, (x, y) in enumerate(product((0, table_width), (0, table_height/2, table_height)))]
    table = Table(width=table_width, height=table_height, balls=balls, pockets=pockets)
    return table


def animate(pockets, logs, flip=False):
    import sys

    import pygame
    from PlanningCore.billiard.visualize import COLOR_MAP

    cloth_color = (202, 222, 235)
    scale = 800 / max([table_width, table_height])
    screen_width = scale * (table_height if flip else table_width)
    screen_height = scale * (table_width if flip else table_height)
    radius = ball_radius * scale
    pocket_r = pocket_radius * scale

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
                rect=(y - pocket_r, x - pocket_r, pocket_r * 2, pocket_r * 2),
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
    from PlanningCore.billiard import init_table
    t = init_table((0,0),[(1,1)])
    # angles = search_optimal_strike(table=t, dt=0.02, dang=0.5)
    # print(angles)
    # shot(
    #     table=t,
    #     v_cue=1,
    #     phi=angles[-1][1],
    #     theta=0,
    #     a=0,
    #     b=0,
    # )
    # simulate(t, dt=0.02, log=True)
    animate(t.pockets, t.log, False)