from PlanningCore.core import constants
from PlanningCore.core.constants import State
from PlanningCore.core.planning import search_optimal_strike
from PlanningCore.core.utils import coordinate_transformation, get_common_tangent_angles, get_line_formula


if __name__ == '__main__':
    from PlanningCore.billiard import animate, init_table
    from PlanningCore.core.simulation import shot, simulate, simulate_event_based
    cue_ball_pos = [-0.9061838325810423, -2.8713336068937214]
    balls_pos = [
        [0.3936766516208451, -2.8422322527697985],
        [0.810796060730406, -2.8907345096430035],
        [0.8544480919162902, -2.560919162905211],
        [-1.2748009848173985, -3.2496512105047186],
    ]
    t = init_table(cue_ball_pos, balls_pos)
    from time import perf_counter
    t1 = perf_counter()
    angles = search_optimal_strike(
        table=t,
        v_cue=1,
        dt=0.02,
        dang=0.5,
        return_once_find=True,
        event_based=True,
    )
    t2 = perf_counter()
    print(t2-t1)
    print(angles)
    shot(
        table=t,
        v_cue=1,
        phi=angles[-1][1],
        theta=0,
        a=0,
        b=0,
    )
    # simulate(t, dt=0.02, log=True)
    simulate_event_based(t, log=True)
    animate(t.pockets, t.log, False)