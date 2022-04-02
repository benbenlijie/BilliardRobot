from PlanningCore.core import search_optimal_strike
from PlanningCore.billiard import init_table


def get_strike_angles(
    cue_ball_pos,
    balls_pos,
    v_cue=1,
    dt=0.2,
    dang=0.5,
    return_once_find=True,
    event_based=True,
):
    table = init_table(cue_ball_pos=cue_ball_pos, balls_pos=balls_pos)
    return search_optimal_strike(
        table=table,
        v_cue=v_cue,
        dt=dt,
        dang=dang,
        return_once_find=return_once_find,
        event_based=event_based,
    )