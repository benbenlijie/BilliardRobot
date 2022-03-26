from math import cos, radians, sin

import pygame

from PlanningCore.billiard import Table, Ball
from PlanningCore.core import Force


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


class Billiard(object):
    def __init__(self, width=660, height=360, friction=0.005, margin=30, color_map=None, n_balls=10):
        self.width = width
        self.height = height
        self.friction = friction
        self.color_map = color_map
        self.n_balls = n_balls

        self.cue_ball = Ball(0, 'white', (width/2, height/2), is_cue=True)
        self.table = Table(width, height, margin, friction, balls=[], pockets=[])

        self.display = None
        self.clock = None

    def init_pygame(self):
        pygame.init()
        self.display = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

    def render(self):
        self.display.fill(self.color_map['gray'])
        pygame.draw.ellipse(
            surface=self.display,
            color=self.color_map['white'],
            rect=(self.cue_ball.x-self.cue_ball.radius, self.cue_ball.y-self.cue_ball.radius, self.cue_ball.radius*2, self.cue_ball.radius*2)
        )
        pygame.display.update()
        self.clock.tick(60)

    def hit(self, force):
        self.cue_ball.apply_force(force)

    def run(self):
        self.init_pygame()
        while True:
            for event in pygame.event.get():
                pass
            move_ball(self.cue_ball)
            self.render()


def move_ball(ball, width=660, height=360, friction=0.005):
    ball.velocity -= friction

    if ball.velocity <= 0:
        ball.velocity = 0
    ball.x = ball.x + ball.velocity * cos(radians(ball.force_angle))
    ball.y = ball.y + ball.velocity * sin(radians(ball.force_angle))

    if ball.x > width - ball.radius:
        ball.x = width - ball.radius
        ball.force_angle = 180 - ball.force_angle
    if ball.x < ball.radius:
        ball.x = ball.radius
        ball.force_angle = 180 - ball.force_angle
    if ball.y > height - ball.radius:
        ball.y = height - ball.radius
        ball.force_angle = 360 - ball.force_angle
    if ball.y < ball.radius:
        ball.y = ball.radius
        ball.force_angle = 360 - ball.force_angle


if __name__ == '__main__':
    from threading import Thread

    billiard = Billiard(color_map=COLOR_MAP)
    t = Thread(target=billiard.run)
    t.start()
    while True:
        m, d = input('Input magnitude and direction of force:').strip().split()
        f = Force(float(m), float(d))
        billiard.hit(f)