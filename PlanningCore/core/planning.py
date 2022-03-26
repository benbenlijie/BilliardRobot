from math import degrees, sqrt, acos

import numpy as np

from PlanningCore.core.utils import get_common_tangent_angles
from PlanningCore.core.simulation import shot, simulate
from PlanningCore.core.constants import State


def search_optimal_strike(table, dt, dang, return_once_find=False):
    """Search optimal strike."""
    angles = []
    for target_ball in table.balls[1:]:
        angle1, angle2 = get_common_tangent_angles(
            cue_ball=table.balls[0],
            target_ball=target_ball,
        )
        for ang in np.arange(angle1, angle2, dang):
            shot(table, phi=ang, v_cue=1)
            if simulate(table, dt=dt):
                if table.balls[0].state == State.pocketed:
                    table.reset_balls()
                    continue
                for ball in table.balls[1:]:
                    if ball.state == State.pocketed:
                        angles.append((ball.no, ang))
                        if return_once_find:
                            table.reset_balls()
                            return angles
            table.reset_balls()
    if not angles:
        cue_ball = table.balls[0]
        target_ball = table.balls[1]
        r1 = np.asarray(cue_ball.pos)
        r2 = np.asarray(target_ball.pos)
        len_r1_r2 = sqrt(((r1 - r2) ** 2).sum())
        angle = degrees(acos((r2[0]-r1[0]) / len_r1_r2))
        if r2[1] < r1[1]:
            angle = -angle
        angles.append((target_ball.no, angle))
    return angles