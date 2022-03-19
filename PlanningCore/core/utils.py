import numpy as np

from PlanningCore.core.constants import ball_radius


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