"""Tests (qui PASSENT) du modèle de simulation : sanity checks du MJCF et du solveur de fermeture."""
import math
import unittest

import numpy as np

from five_bars_mujoco.sim import FiveBarsSim


class TestFiveBarsSim(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim = FiveBarsSim()

    def setUp(self):
        self.sim.reset()

    def test_home_is_closed(self):
        self.assertLess(self.sim.closure_error(), 1e-9)

    def test_settle_reaches_command_and_keeps_chain_closed(self):
        for q1, q4 in [(2.4, 0.9), (1.2, 0.5), (2.0, 1.6)]:
            self.assertTrue(self.sim.settle(q1, q4))
            np.testing.assert_allclose(self.sim.actuated_positions(), [q1, q4], atol=1e-4)
            self.assertLess(self.sim.closure_error(), 1e-6)

    def test_command_is_saturated(self):
        q1, q4 = self.sim.set_command(10.0, -10.0)
        self.assertEqual((q1, q4), (self.sim.ctrl_range("joint_q1")[1], self.sim.ctrl_range("joint_q4")[0]))

    def test_kinematic_closure_matches_dynamic_simulation(self):
        self.assertTrue(self.sim.settle(2.2, 1.3))
        dyn = self.sim.joint_positions()
        kin = FiveBarsSim(self.sim.model_path)
        self.assertTrue(kin.solve_closure(dyn["joint_q1"], dyn["joint_q4"]))
        for j, v in kin.joint_positions().items():
            self.assertAlmostEqual(v, dyn[j], delta=1e-5, msg=j)

    def test_unreachable_configuration_is_reported(self):
        kin = FiveBarsSim(self.sim.model_path)
        # bras croisés : A2 et A4 quasi confondus, |A2A4| < |l2 - l3| -> fermeture impossible
        self.assertFalse(kin.solve_closure(math.radians(30), math.radians(150)))


if __name__ == "__main__":
    unittest.main()
