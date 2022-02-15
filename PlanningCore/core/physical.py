from math import atan, cos, degrees, radians, sin, sqrt


def collision(ball1, ball2, radius):
    dist = ((ball1.x - ball2.x)**2 + (ball1.y - ball2.y)**2)**0.5
    if dist <= radius * 2:
        return True
    else:
        return False


def checkCollision(balls, radius):
    for i in range(len(balls)):
        for j in range(len(balls) - 1, i, -1):
            if collision(balls[i], balls[j], radius):
                if balls[i].x == balls[j].x:
                    angleIncline = 2*90
                else:
                    u1 = balls[i].speed
                    u2 = balls[j].speed

                    balls[i].speed = sqrt(
                        (u1 * cos(radians(balls[i].angle)))**2 + (u2 * sin(radians(balls[j].angle)))**2)
                    balls[j].speed = sqrt(
                        (u2 * cos(radians(balls[j].angle)))**2 + (u1 * sin(radians(balls[i].angle)))**2)

                    tangent = degrees((atan((balls[i].y - balls[j].y)/(balls[i].x - balls[j].x)))) + 90
                    angle = tangent + 90

                    balls[i].angle = (2*tangent - balls[i].angle)
                    balls[j].angle = (2*tangent - balls[j].angle)

                    balls[i].x += (balls[i].speed)*sin(radians(angle))
                    balls[i].y -= (balls[i].speed)*cos(radians(angle))
                    balls[j].x -= (balls[j].speed)*sin(radians(angle))
                    balls[j].y += (balls[j].speed)*cos(radians(angle))


class Force(object):
    def __init__(self, magnitude, direction):
        self.magnitude = magnitude
        self.direction = direction

    def __repr__(self):
        return f'Force(magnitude={self.magnitude}, direction={self.direction})'