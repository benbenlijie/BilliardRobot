from PlanningCore.core import constants
import math
import numpy as np

def getDist(point, line_point1, line_point2):
    A = line_point2[1] - line_point1[1]
    B = line_point1[0] - line_point2[0]
    C = (line_point1[1] - line_point2[1]) * line_point1[0] + (line_point2[0] - line_point1[0]) * line_point1[1]
    distance = np.abs(A * point[0] + B * point[1] + C) / (np.sqrt(A**2 + B**2))
    return distance

def obstacle(index, table, pocket, objectball):
    for ball in table.balls:
        if ball.no == index:
            continue
        dis = getDist(ball.pos, objectball.pos, pocket.pos)
        if dis < constants.ball_radius * 2:
            #补充
            return True
    return False

def findpocket(index, table):
    objectball = table.balls[index]
    for pocket in table.pockets:
        if not obstacle(index, table, pocket, objectball):
            #distance = math.sqrt((objectball.pos[0] - pocket.pos[0]) ** 2 + (objectball.pos[1] - pocket.pos[1]) ** 2)
            r1 = np.asarray(objectball.pos)
            r2 = np.asarray(pocket.pos)
            len_r1_r2 = math.sqrt(((r1 - r2) ** 2).sum())
            alpha = math.acos((r2[0] - r1[0])/ len_r1_r2)
            if r2[1] < r1[1]:
                alpha = -alpha


            return math.degrees(alpha)
    return None
