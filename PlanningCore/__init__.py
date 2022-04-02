from PlanningCore.core import search_optimal_direct_strike, search_optimal_strike
from PlanningCore.billiard import init_table


def get_strike_angles(
    cue_ball_pos: tuple[float, float],
    balls_pos: list[tuple[float, float]],
    v_cue: float = 1,
    dt: float = 0.2,
    dang: float = 0.5,
    return_once_find: bool = True,
    event_based: bool = True,
    direct_strike: bool = False,
) -> list[tuple[int, float, tuple[float, float]]]:
    """
    Get the strike angles

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
        cue_ball_pos: Cue ball pos, (x, y).
        balls_pos: List of other balls' pos, (x, y).
        v_cue: Cue's velocity.
        dt: Discrete time, in sec, need to specify when `event_based` is False.
        dang: Discrete angle, in degree.
        return_once_find: Stop search when find one strike angle that can make ball pocket.
        event_based: Use event based simulation function or discrete time based.
        direct_strike: Whether direct shot the ball or shot the cue ball.

    Returns:
        list[tuple[int, float, tuple[float, float]]]: List of angles found.
            int: First one is the index of ball that need to be hit (for simulation use).
            float: Strike angle, see Notes.
            tuple[float, float]: The ball pos.
    """
    table = init_table(cue_ball_pos=cue_ball_pos, balls_pos=balls_pos)
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