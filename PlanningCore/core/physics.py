from math import atan, cos, degrees, radians, sin, sqrt

import numpy as np

from PlanningCore.core.constants import (
    ball_radius,
    ball_mass,
    cue_mass,
    ball_moment_inertia,
    e_c, f_c,
    State,
    cushion_height,
    u_s,
    u_sp,
    u_r,
    g,
)
from PlanningCore.core.utils import coordinate_rotation, unit_vector, angle, get_rel_velocity


def cue_strike(cue_velocity, phi, theta, a=0, b=0):
    """Strike a ball
                              , - ~  ,
    ◎───────────◎         , '          ' ,
    │           │       ,             ◎    ,
    │      /    │      ,              │     ,
    │     /     │     ,               │ b    ,
    ◎    / phi  ◎     ,           ────┘      ,
    │   /___    │     ,            -a        ,
    │           │      ,                    ,
    │           │       ,                  ,
    ◎───────────◎         ,               '
      bottom cushion        ' - , _ , -
                     ______________________________
                              playing surface

    Args:
        cue_velocity: Initial velocity the cue strike the ball.
        phi: The direction you strike the ball in relation to the bottom cushion.
        theta: How elevated is the cue from the playing surface, in degrees
        a: How much side english should be put on? -1 being rightmost side of ball, +1 being leftmost side of ball.
        b: How much vertical english should be put on? -1 being bottom-most side of ball, +1 being topmost side of ball.

    Returns:
        Velocity and angular velocity of ball after cue strike.
    """

    a *= ball_radius*0.5
    b *= ball_radius*0.5

    phi = radians(phi)
    theta = radians(theta)

    c = np.sqrt(ball_radius ** 2 - a ** 2 - b ** 2)

    # Calculate impact force.
    numerator = 2 * cue_mass * cue_velocity
    temp = a**2 + (b*np.cos(theta))**2 + (c*np.cos(theta))**2 - 2*b*c*np.cos(theta)*np.sin(theta)
    denominator = 1 + ball_mass / cue_mass + 5 / 2 / ball_radius ** 2 * temp
    force = numerator/denominator

    v_ball = -force / ball_mass * np.array([0, np.cos(theta), 0])
    w_ball = force/ball_moment_inertia * np.array([-c*np.sin(theta) + b*np.cos(theta), a*np.sin(theta), -a*np.cos(theta)])

    # Rotate to table reference.
    rot_angle = phi + np.pi/2
    v_ball = coordinate_rotation(v_ball, rot_angle)
    w_ball = coordinate_rotation(w_ball, rot_angle)

    return v_ball, w_ball


def ball_ball_collision(ball1_rvw, ball2_rvw):
    r1, r2 = ball1_rvw[0], ball2_rvw[0]
    v1, v2 = ball1_rvw[1], ball2_rvw[1]

    v_rel = v1 - v2
    v_mag = np.linalg.norm(v_rel)

    n = unit_vector(r2 - r1)
    t = coordinate_rotation(n, np.pi/2)

    beta = angle(v_rel, n)

    ball1_rvw[1] = t * v_mag * np.sin(beta) + v2
    ball2_rvw[1] = n * v_mag * np.cos(beta) + v2

    return ball1_rvw, ball2_rvw


def ball_cushion_collision(rvw, normal):
    """Inhwan Han (2005) `Dynamics in Carom and Three Cushion Billiards`"""

    # Orient the normal, so it points away from playing surface.
    normal = normal if np.dot(normal, rvw[1][:2]) > 0 else -normal

    # Change from the table frame to the cushion frame. The cushion frame is defined by
    # the normal vector is parallel with <1,0,0>.
    psi = angle(normal)
    rvw_R = coordinate_rotation(rvw.T, -psi).T

    # The incidence angle--called theta_0 in paper.
    phi = angle(rvw_R[1]) % (2*np.pi)

    # Get mu and e
    e = e_c
    mu = f_c

    # Depends on height of cushion relative to ball
    theta_a = np.arcsin(cushion_height / ball_radius - 1)

    # Eqs 14
    sx = rvw_R[1, 0] * np.sin(theta_a) - rvw_R[1, 2] * np.cos(theta_a) + ball_radius * rvw_R[2, 1]
    sy = -rvw_R[1, 1] - ball_radius * rvw_R[2, 2] * np.cos(theta_a) + ball_radius * rvw_R[2, 0] * np.sin(theta_a)
    c = rvw_R[1, 0]*np.cos(theta_a) # 2D assumption

    # Eqs 16
    I = 2 / 5 * ball_mass * ball_radius ** 2
    A = 7 / 2 / ball_mass
    B = 1 / ball_mass

    # Eqs 17 & 20
    PzE = (1 + e)*c/B
    PzS = np.sqrt(sx**2 + sy**2)/A

    if PzS <= PzE:
        # Sliding and sticking case
        PX = -sx/A*np.sin(theta_a) - (1+e)*c/B*np.cos(theta_a)
        PY = sy/A
        PZ = sx/A*np.cos(theta_a) - (1+e)*c/B*np.sin(theta_a)
    else:
        # Forward sliding case
        PX = -mu*(1+e)*c/B*np.cos(phi)*np.sin(theta_a) - (1+e)*c/B*np.cos(theta_a)
        PY = mu*(1+e)*c/B*np.sin(phi)
        PZ = mu*(1+e)*c/B*np.cos(phi)*np.cos(theta_a) - (1+e)*c/B*np.sin(theta_a)

    # Update velocity.
    rvw_R[1, 0] += PX / ball_mass
    rvw_R[1, 1] += PY / ball_mass
    #rvw_R[1,2] += PZ/m

    # Update angular velocity
    rvw_R[2, 0] += -ball_radius / I * PY * np.sin(theta_a)
    rvw_R[2, 1] += ball_radius / I * (PX * np.sin(theta_a) - PZ * np.cos(theta_a))
    rvw_R[2, 2] += ball_radius / I * PY * np.cos(theta_a)

    # Change back to table reference frame
    rvw = coordinate_rotation(rvw_R.T, psi).T

    return rvw


def get_slide_time(rvw):
    return 2*np.linalg.norm(get_rel_velocity(rvw)) / (7*u_s*g)


def get_roll_time(rvw):
    _, v, _ = rvw
    return np.linalg.norm(v) / (u_r*g)


def get_spin_time(rvw):
    _, _, w = rvw
    return np.abs(w[2]) * 2/5*ball_radius/u_sp/g


def evolve_ball_motion(state, rvw, t):
    if state == State.stationary:
        return rvw, state

    if state == State.sliding:
        t_slide = get_slide_time(rvw)

        if t >= t_slide:
            rvw = evolve_slide_state(rvw, t_slide)
            state = State.rolling
            t -= t_slide
        else:
            return evolve_slide_state(rvw, t), State.sliding

    if state == State.rolling:
        t_roll = get_roll_time(rvw)

        if t >= t_roll:
            rvw = evolve_roll_state(rvw, t_roll)
            state = State.spinning
            t -= t_roll
        else:
            return evolve_roll_state(rvw, t), State.rolling

    if state == State.spinning:
        t_spin = get_spin_time(rvw)

        if t >= t_spin:
            return evolve_spin_state(rvw, t_spin), State.stationary
        else:
            return evolve_spin_state(rvw, t), State.spinning


def evolve_slide_state(rvw, t):
    # Angle of initial velocity in table frame
    phi = angle(rvw[1])

    rvw_t = coordinate_rotation(rvw.T, -phi).T

    # Relative velocity unit vector in ball frame.
    u_0 = coordinate_rotation(unit_vector(get_rel_velocity(rvw)), -phi)

    # Calculate quantities according to the ball frame. NOTE w_B in this code block
    # is only accurate of the x and y evolution of angular velocity. z evolution of
    # angular velocity is done in the next block

    rvw_t = np.array([
        np.array([rvw_t[1, 0]*t - 1/2*u_s*g*t**2 * u_0[0], -1/2*u_s*g*t**2 * u_0[1], 0]),
        rvw_t[1] - u_s*g*t*u_0,
        rvw_t[2] - 5 / 2 / ball_radius * u_s * g * t * np.cross(u_0, np.array([0, 0, 1]))
    ])

    # This transformation governs the z evolution of angular velocity
    rvw_t = evolve_spin_state(rvw_t, t)

    # Rotate to table reference
    rvw_t = coordinate_rotation(rvw_t.T, phi).T
    rvw_t[0] += rvw[0]

    return rvw_t


def evolve_roll_state(rvw, t):
    r_0, v_0, w_0 = rvw

    v_0_unit = unit_vector(v_0)

    r_t = r_0 + v_0 * t - 1/2*u_r*g*t**2 * v_0_unit
    v_t = v_0 - u_r*g*t * v_0_unit
    w_t = coordinate_rotation(v_t / ball_radius, np.pi / 2)

    # Independently evolve the z spin.
    w_t[2] = evolve_spin_state(rvw, t)[2, 2]

    # This transformation governs the z evolution of angular velocity.
    return np.asarray([r_t, v_t, w_t])


def evolve_spin_state(rvw, t):
    w_0 = rvw[2]

    # Always decay towards 0, whether spin is +ve or -ve.
    sign = 1 if w_0[2] > 0 else -1

    # Decay to 0, but not past.
    decay = min([np.abs(w_0[2]), 5 / 2 / ball_radius * u_sp * g * t])

    rvw[2, 2] -= sign * decay
    return rvw


class Force(object):
    def __init__(self, magnitude, direction):
        self.magnitude = magnitude
        self.direction = direction

    def __repr__(self):
        return f'Force(magnitude={self.magnitude}, direction={self.direction})'


if __name__ == '__main__':
    cue_strike(1, 90, 5, 0, 0)