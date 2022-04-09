from PlanningCore.core import search_optimal_direct_strike, search_optimal_strike
from PlanningCore.billiard import init_table


def get_strike_angles(
    balls_pos,
    cue_ball_pos=(0, 0),
    robot_pos=(0, -2),
    v_cue=1,
    dt=0.2,
    dang=0.5,
    return_once_find=True,
    event_based=True,
    direct_strike=False,
):
    """
    Get the strike angles.

    Notes:
        The strike angle is phi:
        ----------------------x
        |     \  ) phi
        |      \
        |       \|
        |       hit point
        |
        |
        |
        y

    Args:
        balls_pos (list[tuple[float, float]]): List of other balls' pos, (x, y).
        v_cue (float): Cue's velocity.
        cue_ball_pos (tuple[float, float]): Cue ball pos, (x, y).
        robot_pos: Robot position.
        dt (float): Discrete time, in sec, need to specify when `event_based` is False.
        dang (float): Discrete angle, in degree.
        return_once_find (bool): Stop search when find one strike angle that can make ball pocket.
        event_based (bool): Use event based simulation function or discrete time based.
        direct_strike (bool): Whether direct shot the ball or shot the cue ball.

    Returns:
        list[tuple[int, float, tuple[float, float]]]: List of angles found.
            int: Index of ball that need to be hit (for simulation use).
            float: Strike angle, see Notes.
            tuple[float, float]: Pos of ball that need to be hit.
    """
    table = init_table(cue_ball_pos=cue_ball_pos, balls_pos=balls_pos, robot_pos=robot_pos)
    if direct_strike:
        angles = search_optimal_direct_strike(
            table=table,
            v_cue=v_cue,
            dt=dt,
            return_once_find=return_once_find,
            event_based=event_based,
        )
    else:
        angles = search_optimal_strike(
            table=table,
            v_cue=v_cue,
            dt=dt,
            dang=dang,
            return_once_find=return_once_find,
            event_based=event_based,
        )
    return angles