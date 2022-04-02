import sys

import pygame

from PlanningCore.core import constants as c


COLOR_MAP = {
    'black': (23, 32, 42),
    'white': (236, 240, 241),
    'gray': (123, 125, 125),
    'yellow': (244, 208, 63),
    'blue': (52, 52, 153),
    'red': (203, 67, 53),
    'purple': (136, 78, 160),
    'orange': (230, 126, 34),
    'green': (40, 180, 99),
    'brown': (100, 30, 22),
}


def animate(pockets, logs, flip=False):
    cloth_color = (202, 222, 235)
    scale = 800 / max([c.table_width, c.table_height])
    screen_width = scale * (c.table_height if flip else c.table_width)
    screen_height = scale * (c.table_width if flip else c.table_height)
    radius = c.ball_radius * scale
    pocket_r = c.pocket_radius * scale

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
                color=COLOR_MAP[ball['color']] if ball['state'] != c.State.pocketed else COLOR_MAP['green'],
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