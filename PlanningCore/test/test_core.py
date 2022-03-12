import unittest
from itertools import product

import numpy as np
import pooltool.physics as ref
from time import perf_counter

from PlanningCore.core import physics as my
from PlanningCore.core import constants as c


def get_random_rvw():
    return np.random.rand(3, 3)


class TestPhysics(unittest.TestCase):

    def setUp(self) -> None:
        self.test_rvw = [get_random_rvw() for _ in range(10)]
        self.threshold = 1e-5

    def test_cue_strike(self):
        for cue_velocity, phi, theta in product((0.1, 0.5, 1), (0, 45, 90), (0, 15, 45)):
            v_ref, w_ref = ref.cue_strike(
                m=c.ball_mass,
                M=c.cue_mass,
                R=c.ball_radius,
                V0=cue_velocity,
                phi=phi,
                theta=theta,
                a=0,
                b=0,
            )
            v_my, w_my = my.cue_strike(
                cue_velocity=cue_velocity,
                phi=phi,
                theta=theta,
            )
            diff = np.abs(v_ref - v_my).sum() + np.abs(w_ref - w_my).sum()
            self.assertTrue(diff < self.threshold)

    def test_ball_ball_collision(self):
        pass

    def test_ball_cushion_collision(self):
        pass

    def test_get_slide_time(self):
        for rvw in self.test_rvw:
            t_ref = ref.get_slide_time(rvw, c.ball_radius, c.u_s, c.g)
            t_my = my.get_slide_time(rvw)
            diff = np.abs(t_ref - t_my)
            self.assertTrue(diff < self.threshold)

    def test_get_roll_time(self):
        for rvw in self.test_rvw:
            t_ref = ref.get_roll_time(rvw, c.u_r, c.g)
            t_my = my.get_roll_time(rvw)
            diff = np.abs(t_ref - t_my)
            self.assertTrue(diff < self.threshold)

    def test_get_spin_time(self):
        for rvw in self.test_rvw:
            t_ref = ref.get_spin_time(rvw, c.ball_radius, c.u_sp, c.g)
            t_my = my.get_spin_time(rvw)
            diff = np.abs(t_ref - t_my)
            self.assertTrue(diff < self.threshold)

    def test_evolve_ball_motion(self):
        for rvw in self.test_rvw:
            for state in c.State.all:
                for t in (0.1, 0.2, 0.3, 0.4, 0.5):
                    rvw_ref, state_ref = ref.evolve_ball_motion(
                        state=state,
                        rvw=rvw,
                        R=c.ball_radius,
                        m=c.ball_mass,
                        u_s=c.u_s,
                        u_sp=c.u_sp,
                        u_r=c.u_r,
                        g=c.g,
                        t=t,
                    )
                    rvw_my, state_my = my.evolve_ball_motion(
                        state=state,
                        rvw=rvw,
                        t=t,
                    )
                    diff = np.abs(rvw_ref - rvw_my).sum()
                    self.assertTrue(diff < self.threshold)
                    self.assertTrue(state_ref == state_my)

    def test_evolve_slide_state(self):
        for rvw in self.test_rvw:
            for t in (0.1, 0.2, 0.3, 0.4, 0.5):
                rvw_ref = ref.evolve_slide_state(
                    rvw=rvw,
                    R=c.ball_radius,
                    m=c.ball_mass,
                    u_s=c.u_s,
                    u_sp=c.u_sp,
                    g=c.g,
                    t=t,
                )
                rvw_my = my.evolve_slide_state(
                    rvw=rvw,
                    t=t,
                )
                diff = np.abs(rvw_ref - rvw_my).sum()
                self.assertTrue(diff < self.threshold)

    def test_evolve_roll_state(self):
        for rvw in self.test_rvw:
            for t in (0.1, 0.2, 0.3, 0.4, 0.5):
                rvw_ref = ref.evolve_roll_state(
                    rvw=rvw,
                    R=c.ball_radius,
                    u_r=c.u_r,
                    u_sp=c.u_sp,
                    g=c.g,
                    t=t,
                )
                rvw_my = my.evolve_roll_state(
                    rvw=rvw,
                    t=t,
                )
                diff = np.abs(rvw_ref - rvw_my).sum()
                self.assertTrue(diff < self.threshold)

    def test_evolve_spin_state(self):
        for rvw in self.test_rvw:
            for t in (0.1, 0.2, 0.3, 0.4, 0.5):
                rvw_ref = ref.evolve_perpendicular_spin_state(
                    rvw=rvw,
                    R=c.ball_radius,
                    u_sp=c.u_sp,
                    g=c.g,
                    t=t,
                )
                rvw_my = my.evolve_spin_state(
                    rvw=rvw,
                    t=t,
                )
                diff = np.abs(rvw_ref - rvw_my).sum()
                self.assertTrue(diff < self.threshold)


if __name__ == '__main__':

    unittest.main()