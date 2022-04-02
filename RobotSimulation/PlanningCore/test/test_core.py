import unittest
from itertools import product

import numpy as np
import pooltool.physics as ref_physics
import pooltool.utils as ref_utils

from PlanningCore.core import physics as my_physics
from PlanningCore.core import utils as my_utils
from PlanningCore.core import constants as c


def get_random_rvw():
    return np.random.rand(3, 3)


class TestPhysics(unittest.TestCase):

    def setUp(self) -> None:
        self.test_rvw = [get_random_rvw() for _ in range(10)]
        self.threshold = 1e-5

    def test_cue_strike(self):
        for cue_velocity, phi, theta in product((0.1, 0.5, 1), (0, 45, 90), (0, 15, 45)):
            v_ref, w_ref = ref_physics.cue_strike(
                m=c.ball_mass,
                M=c.cue_mass,
                R=c.ball_radius,
                V0=cue_velocity,
                phi=phi,
                theta=theta,
                a=0,
                b=0,
            )
            v_my, w_my = my_physics.cue_strike(
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
            t_ref = ref_physics.get_slide_time(rvw, c.ball_radius, c.u_s, c.g)
            t_my = my_physics.get_slide_time(rvw)
            diff = np.abs(t_ref - t_my)
            self.assertTrue(diff < self.threshold)

    def test_get_roll_time(self):
        for rvw in self.test_rvw:
            t_ref = ref_physics.get_roll_time(rvw, c.u_r, c.g)
            t_my = my_physics.get_roll_time(rvw)
            diff = np.abs(t_ref - t_my)
            self.assertTrue(diff < self.threshold)

    def test_get_spin_time(self):
        for rvw in self.test_rvw:
            t_ref = ref_physics.get_spin_time(rvw, c.ball_radius, c.u_sp, c.g)
            t_my = my_physics.get_spin_time(rvw)
            diff = np.abs(t_ref - t_my)
            self.assertTrue(diff < self.threshold)

    def test_evolve_ball_motion(self):
        for rvw in self.test_rvw:
            for state in c.State.all.keys():
                for t in (0.1, 0.2, 0.3, 0.4, 0.5):
                    rvw_ref, state_ref = ref_physics.evolve_ball_motion(
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
                    rvw_my, state_my = my_physics.evolve_ball_motion(
                        pockets=[],
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
                rvw_ref = ref_physics.evolve_slide_state(
                    rvw=rvw,
                    R=c.ball_radius,
                    m=c.ball_mass,
                    u_s=c.u_s,
                    u_sp=c.u_sp,
                    g=c.g,
                    t=t,
                )
                rvw_my = my_physics.evolve_slide_state(
                    rvw=rvw,
                    t=t,
                )
                diff = np.abs(rvw_ref - rvw_my).sum()
                self.assertTrue(diff < self.threshold)

    def test_evolve_roll_state(self):
        for rvw in self.test_rvw:
            for t in (0.1, 0.2, 0.3, 0.4, 0.5):
                rvw_ref = ref_physics.evolve_roll_state(
                    rvw=rvw,
                    R=c.ball_radius,
                    u_r=c.u_r,
                    u_sp=c.u_sp,
                    g=c.g,
                    t=t,
                )
                rvw_my = my_physics.evolve_roll_state(
                    rvw=rvw,
                    t=t,
                )
                diff = np.abs(rvw_ref - rvw_my).sum()
                self.assertTrue(diff < self.threshold)

    def test_evolve_spin_state(self):
        for rvw in self.test_rvw:
            for t in (0.1, 0.2, 0.3, 0.4, 0.5):
                rvw_ref = ref_physics.evolve_perpendicular_spin_state(
                    rvw=rvw,
                    R=c.ball_radius,
                    u_sp=c.u_sp,
                    g=c.g,
                    t=t,
                )
                rvw_my = my_physics.evolve_spin_state(
                    rvw=rvw,
                    t=t,
                )
                diff = np.abs(rvw_ref - rvw_my).sum()
                self.assertTrue(diff < self.threshold)


class TestUtils(unittest.TestCase):

    def setUp(self) -> None:
        self.test_rvw = [get_random_rvw() for _ in range(10)]
        self.threshold = 1e-5

    def test_angle(self):
        for rvw in self.test_rvw:
            ref = ref_utils.angle(rvw[1], tmp := get_random_rvw()[1])
            my = my_utils.angle(rvw[1], tmp)
            diff = np.abs(ref - my).sum()
            self.assertTrue(diff < self.threshold)

    def test_coordinate_rotation(self):
        for rvw in self.test_rvw:
            for phi in (0, 45, 90):
                ref = ref_utils.coordinate_rotation(rvw[1], phi)
                my = my_utils.coordinate_rotation(rvw[1], phi)
                diff = np.abs(ref - my).sum()
                self.assertTrue(diff < self.threshold)

    def test_unit_vector(self):
        for rvw in self.test_rvw:
            for vector, handle_zero in product(rvw, (True, False)):
                ref = ref_utils.unit_vector(vector, handle_zero)
                my = my_utils.unit_vector(vector, handle_zero)
                diff = np.abs(ref - my).sum()
                self.assertTrue(diff < self.threshold)

    def test_get_rel_velocity(self):
        for rvw in self.test_rvw:
            ref = ref_utils.get_rel_velocity(rvw, c.ball_radius)
            my = my_utils.get_rel_velocity(rvw)
            diff = np.abs(ref - my).sum()
            self.assertTrue(diff < self.threshold)


if __name__ == '__main__':

    unittest.main()