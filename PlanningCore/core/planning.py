import numpy as np

from PlanningCore.core.utils import get_common_tangent_angles
from PlanningCore.core.simulation import shot, simulate
from PlanningCore.core.constants import State


def search_optimal_strike(table, dt, dang):
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
            table.reset_balls()
    return angles