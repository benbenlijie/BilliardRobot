from math import acos, degrees, sqrt

import numpy as np

from PlanningCore.core.utils import get_angle_range, get_common_tangent_angles
from PlanningCore.core.simulation import shot, simulate, simulate_event_based
from PlanningCore.core.constants import State


# TODO: sort the ball (which one is most likely pocket)
def search_optimal_strike(
        table,
        v_cue=1,
        dt=0.02,
        dang=0.5,
        return_once_find=False,
        event=False
):
    """Search optimal strike."""
    simulate_func = simulate_event_based if event else simulate
    simulate_args = ({'return_once_pocket': True}
                     if event else
                     {'dt': dt, 'no_ball_cushion': True, 'return_once_pocket': True})
    angles = []
    for target_ball in table.balls[1:]:
        angle1, angle2 = get_common_tangent_angles(
            cue_ball=table.balls[0],
            target_ball=target_ball,
        )
        for ang in get_angle_range(angle1, angle2, dang):
            shot(table, phi=ang, v_cue=v_cue)
            if simulate_func(table, **simulate_args):
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