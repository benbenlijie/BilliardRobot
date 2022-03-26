from math import acos, atan, degrees, sqrt

import numpy as np

from PlanningCore.core import ball_radius, table_width, table_height


def angle(v2, v1=(1, 0)):
    """Calculates counter-clockwise angle of the projections of v1 and v2 onto the x-y plane."""
    ang = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])

    return 2*np.pi + ang if ang < 0 else ang


def coordinate_rotation(v, phi):
    rotation = np.array(
        [
            [np.cos(phi), -np.sin(phi), 0],
            [np.sin(phi), np.cos(phi), 0],
            [0, 0, 1],
        ]
    )
    return np.dot(rotation, v)


def unit_vector(vector, handle_zero=True):
    if len(vector.shape) > 1:
        norm = np.linalg.norm(vector, axis=1, keepdims=True)
        if handle_zero:
            norm[(norm == 0).all(axis=1), :] = 1
        return vector / norm
    else:
        norm = np.linalg.norm(vector)
        if norm == 0 and handle_zero:
            norm = 1
        return vector / norm


def get_rel_velocity(rvw):
    _, v, w = rvw
    return v + ball_radius * np.cross(np.array([0, 0, 1]), w)


def is_pocket(ball_pos, pocket):
    return sqrt(
        (ball_pos[0] - pocket.pos[0]) ** 2
        + (ball_pos[1] - pocket.pos[1]) ** 2
    ) < pocket.radius


def get_common_tangent_angles(cue_ball, target_ball):
    r1 = np.asarray(cue_ball.pos)
    r2 = np.asarray(target_ball.pos)
    len_r1_r2 = sqrt(((r1 - r2) ** 2).sum())
    alpha = acos(2 * cue_ball.radius / len_r1_r2)
    if r2[1] - r1[1] == 0:
        beta = 0
    else:
        beta = atan((r2[0] - r1[0]) / (r2[1] - r1[1]))
    angle1 = degrees(alpha - beta)
    angle2 = degrees(np.pi - alpha - beta)
    return sorted([angle1, angle2])


def coordinate_transformation(pos):
    return pos[0] + table_width/2, pos[1] + table_height/2