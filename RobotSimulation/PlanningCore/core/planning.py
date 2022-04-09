from math import acos, degrees, sqrt

import numpy as np

from PlanningCore.core.utils import (
    coordinate_transformation_inverse,
    get_angle_range,
    get_common_tangent_angles,
    get_vector_angles,
)
from PlanningCore.core.simulation import shot, simulate, simulate_event_based
from PlanningCore.core.constants import State


def search_optimal_strike(
    table,
    v_cue=1,
    dt=0.02,
    dang=0.5,
    return_once_find=False,
    event_based=False,
):
    """Search optimal strike."""
    simulate_func = simulate_event_based if event_based else simulate
    simulate_args = ({'return_once_pocket': True}
                     if event_based else
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
                        table.reset_balls()
                        angles.append((0, ang, coordinate_transformation_inverse(table.balls[0].pos)))
                        if return_once_find:
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
        angles.append((0, angle, coordinate_transformation_inverse(table.balls[0].pos)))
    return angles


def search_optimal_direct_strike(
    table,
    v_cue=1,
    dt=0.02,
    return_once_find=False,
    event_based=False,
):
    """Search optimal direct strike."""
    simulate_func = simulate_event_based if event_based else simulate
    simulate_args = ({'return_once_pocket': True}
                     if event_based else
                     {'dt': dt, 'no_ball_cushion': True, 'return_once_pocket': True})
    results = []
    for i, ball in enumerate(table.balls[1:], 1):
        angles = find_pocket_angles(i, table)
        for angle in angles:
            shot(table, phi=angle, v_cue=v_cue, ball_index=i)
            if simulate_func(table, **simulate_args):
                if table.balls[i].state == State.pocketed:
                    table.reset_balls()
                    results.append((i, angle, coordinate_transformation_inverse(table.balls[i].pos)))
                    if return_once_find:
                        return results
            table.reset_balls()

    if not results:
        pocket = table.pockets[0]
        target_ball = table.balls[1]
        r1 = np.asarray(pocket.pos)
        r2 = np.asarray(target_ball.pos)
        len_r1_r2 = sqrt(((r1 - r2) ** 2).sum())
        angle = degrees(acos((r2[0]-r1[0]) / len_r1_r2))
        if r2[1] < r1[1]:
            angle = -angle
        results.append([1, angle, coordinate_transformation_inverse(target_ball.pos)])
    return results


def get_distance(point, line_point1, line_point2):
    A = line_point2[1] - line_point1[1]
    B = line_point1[0] - line_point2[0]
    C = (line_point1[1] - line_point2[1]) * line_point1[0] + (line_point2[0] - line_point1[0]) * line_point1[1]
    distance = np.abs(A*point[0] + B*point[1] + C) / (np.sqrt(A**2 + B**2))
    return distance


def obstacle(index, table, pocket, target_ball):
    for i, ball in enumerate(table.balls):
        if i == index:
            continue
        dist = get_distance(ball.pos, target_ball.pos, pocket.pos)
        if dist < ball.radius * 2:
            if (
                pocket.pos[0] <= ball.pos[0] <= target_ball.pos[0]
                or pocket.pos[0] >= ball.pos[0] >= target_ball.pos[0]
            ):
                return True
    return False


def sort_pockets(pockets, ball_pos):
    ball_pos = np.asarray(ball_pos)
    dist = [
        ((np.asarray(pocket.pos) - ball_pos) ** 2).sum()
        for pocket in pockets
    ]
    sorted_pockets = sorted(zip(pockets, dist), key=lambda x: x[1])
    return [pocket for pocket, _ in sorted_pockets]


def find_pocket_angles(index, table):
    target_ball = table.balls[index]
    angles = []
    sorted_pockets = sort_pockets(table.pockets, target_ball.pos)
    for pocket in sorted_pockets:
        if (
            not obstacle(index, table, pocket, target_ball)
            and get_vector_angles(table.robot.pos, target_ball.pos, pocket.pos) < 75
        ):
            r1 = np.asarray(target_ball.pos)
            r2 = np.asarray(pocket.pos)
            len_r1_r2 = sqrt(((r1 - r2) ** 2).sum())
            alpha = acos((r2[0] - r1[0])/ len_r1_r2)
            if r2[1] < r1[1]:
                alpha = -alpha
            angles.append(degrees(alpha))
    return angles