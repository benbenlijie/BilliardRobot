import numpy as np
from math import *

width = 660
height = 360
margin = 30
friction = 0.005
radius = 10

class Ball:
    def __init__(self, ballNum, angle):
        self.ballNum = ballNum
        self.pos = np.zeros(2, dtype=float)
        self.speed = np.zeros(2, dtype=float)
        self.angle = angle

    def apply_force(self, force):
        '''
        受到力之后得到速度和角度
        '''
        pass

    def move(self):
        '''
        这里的x和y不是球心，是这个圆的外界正方形的左下角
        :return:
        '''
        self.speed -= friction
        if self.speed <= 0:
            self.speed = 0
        self.x = self.y + self.speed*cos(radians(self.angle))
        self.y = self.y + self.speed * sin(radians(self.angle))

        if not (self.x < width - radius - margin):
            self.x = width - radius - margin
            self.angle = 180 - self.angle
        if not(radius + margin < self.x):
            self.x = radius + margin
            self.angle = 180 - self.angle
        if not (self.y < height - radius - margin):
            self.y = height - radius - margin
            self.angle = 360 - self.angle
        if not(radius + margin < self.y):
            self.y = radius + margin
            self.angle = 360 - self.angle

class Pockets:
    def __init__(self, x, y, color):
        self.r = margin / 2
        self.x = x + self.r + 10
        self.y = y + self.r + 10
        self.color = color

    # Checks if ball has entered the Hole
    def checkPut(self):
        global balls
        ballsCopy = balls[:]
        for i in range(len(balls)):
            dist = ((self.x - balls[i].x) ** 2 + (self.y - balls[i].y) ** 2) ** 0.5
            if dist < self.r + radius:
                if balls[i] in ballsCopy:
                    ballsCopy.remove(balls[i])

        balls = ballsCopy[:]
