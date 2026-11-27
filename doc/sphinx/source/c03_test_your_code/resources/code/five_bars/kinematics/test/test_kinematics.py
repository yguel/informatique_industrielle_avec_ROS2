"""Tests unitaires (unittest) des modèles géométriques direct/inverse du 5 barres.

La vérité terrain est fournie par la simulation MuJoCo HEADLESS (aucun affichage) :
on envoie une consigne (q1, q4) aux servos simulés, on attend l'équilibre, puis on
lit la position du site 'pen_tip' (pointe du stylo) — la boucle étant fermée par la
contrainte MuJoCo, c'est une référence indépendante de votre modèle.

Ces tests ÉCHOUENT tant que five_bars_kinematics/kinematics.py n'est pas implémenté
(la classe TestSimulationHarness, elle, doit passer : elle valide le banc de test).

Lancement :
    colcon test --packages-select five_bars_kinematics && colcon test-result --verbose
    # ou directement :
    python3 -m unittest discover -s src/five_bars_kinematics/test -p "test_*.py" -v
"""
import math
import unittest
from dataclasses import asdict

import numpy as np

from five_bars_kinematics import Geometry, forward_kinematics, inverse_kinematics
from five_bars_mujoco.sim import FiveBarsSim

# Configurations articulaires de test (degrés) : même mode d'assemblage que le robot,
# loin des singularités.
Q_GRID_DEG = [(q1, q4) for q1 in (90.0, 110.0, 130.0, 150.0) for q4 in (20.0, 40.0, 60.0, 80.0)]
# Points à atteindre (m) : une zone de dessin rectangulaire devant le robot.
XY_TARGETS = [(x, y) for x in (0.02, 0.04, 0.06, 0.08) for y in (0.13, 0.15, 0.17)]

POS_TOL = 1e-4      # 0.1 mm entre modèle et simulation
ANGLE_TOL = 1e-3    # rad
REACH_TOL = 5e-4    # 0.5 mm après asservissement simulé


def wrap(a: float) -> float:
    return math.atan2(math.sin(a), math.cos(a))


class MujocoTestCase(unittest.TestCase):
    """Fournit une simulation MuJoCo headless et la géométrie extraite du modèle."""

    @classmethod
    def setUpClass(cls):
        cls.sim = FiveBarsSim()
        cls.geometry = Geometry(**asdict(cls.sim.geometry))

    def simulate(self, q1: float, q4: float):
        """Asservit (q1, q4) dans MuJoCo depuis 'home' ; renvoie (q1, q4) mesurés et (x, y) du stylo."""
        self.sim.reset()
        self.assertTrue(self.sim.settle(q1, q4), "la simulation n'a pas convergé")
        self.assertLess(self.sim.closure_error(), 1e-6, "chaîne non fermée dans la simulation")
        q = self.sim.actuated_positions()
        pen = self.sim.pen_position()
        return (float(q[0]), float(q[1])), (float(pen[0]), float(pen[1]))


class TestSimulationHarness(MujocoTestCase):
    """Vérifie le banc de test lui-même (ces tests doivent PASSER)."""

    def test_home_pen_position_matches_cad(self):
        self.sim.reset()
        pen = self.sim.pen_position()
        # alésage du porte-stylo mesuré sur la CAO : (73.45, 202.20) mm
        np.testing.assert_allclose(pen[:2], [0.07345, 0.20220], atol=1e-3)

    def test_simulation_tracks_commands(self):
        (q1, q4), _ = self.simulate(math.radians(120), math.radians(50))
        self.assertAlmostEqual(q1, math.radians(120), delta=1e-4)
        self.assertAlmostEqual(q4, math.radians(50), delta=1e-4)


class TestForwardKinematics(MujocoTestCase):

    def test_home_configuration(self):
        self.sim.reset()
        q = self.sim.actuated_positions()
        pen = self.sim.pen_position()
        result = forward_kinematics(float(q[0]), float(q[1]), self.geometry)
        self.assertIsNotNone(result)
        np.testing.assert_allclose(result, pen[:2], atol=POS_TOL)

    def test_matches_mujoco_simulation(self):
        for q1d, q4d in Q_GRID_DEG:
            with self.subTest(q1_deg=q1d, q4_deg=q4d):
                (q1, q4), pen = self.simulate(math.radians(q1d), math.radians(q4d))
                result = forward_kinematics(q1, q4, self.geometry)
                self.assertIsNotNone(result, "configuration atteignable déclarée impossible")
                np.testing.assert_allclose(result, pen, atol=POS_TOL)

    def test_pen_offset_is_taken_into_account(self):
        """Le stylo n'est PAS en A3 : un modèle qui l'oublie doit échouer ici."""
        self.sim.reset()
        q = self.sim.actuated_positions()
        x, y = forward_kinematics(float(q[0]), float(q[1]), self.geometry)
        a3 = self.sim.data.site("A3_link2").xpos[:2]
        offset = math.hypot(self.geometry.pen_dx, self.geometry.pen_dy)
        self.assertAlmostEqual(math.hypot(x - a3[0], y - a3[1]), offset, delta=POS_TOL)

    def test_unassemblable_configuration_returns_none(self):
        # Bras croisés : A2 et A4 quasi confondus -> |A2A4| < |l2 - l3|
        self.assertIsNotNone(forward_kinematics(math.radians(110), math.radians(60), self.geometry))
        self.assertIsNone(forward_kinematics(math.radians(30), math.radians(150), self.geometry))


class TestInverseKinematics(MujocoTestCase):

    def test_matches_mujoco_simulation(self):
        for q1d, q4d in Q_GRID_DEG:
            with self.subTest(q1_deg=q1d, q4_deg=q4d):
                (q1, q4), (x, y) = self.simulate(math.radians(q1d), math.radians(q4d))
                result = inverse_kinematics(x, y, self.geometry)
                self.assertIsNotNone(result, "point atteignable déclaré inatteignable")
                self.assertAlmostEqual(wrap(result[0] - q1), 0.0, delta=ANGLE_TOL)
                self.assertAlmostEqual(wrap(result[1] - q4), 0.0, delta=ANGLE_TOL)

    def test_reaches_targets_in_simulation(self):
        """IK -> consignes des servos simulés -> le stylo doit arriver sur la cible."""
        for x, y in XY_TARGETS:
            with self.subTest(x=x, y=y):
                result = inverse_kinematics(x, y, self.geometry)
                self.assertIsNotNone(result)
                _, pen = self.simulate(*result)
                self.assertLess(math.hypot(pen[0] - x, pen[1] - y), REACH_TOL)

    def test_inverse_of_forward_is_identity(self):
        for q1d, q4d in Q_GRID_DEG:
            with self.subTest(q1_deg=q1d, q4_deg=q4d):
                q1, q4 = math.radians(q1d), math.radians(q4d)
                x, y = forward_kinematics(q1, q4, self.geometry)
                r1, r4 = inverse_kinematics(x, y, self.geometry)
                self.assertAlmostEqual(wrap(r1 - q1), 0.0, delta=1e-9)
                self.assertAlmostEqual(wrap(r4 - q4), 0.0, delta=1e-9)

    def test_unreachable_point_returns_none(self):
        self.assertIsNotNone(inverse_kinematics(0.07, 0.17, self.geometry))
        self.assertIsNone(inverse_kinematics(0.5, 0.5, self.geometry))   # trop loin
        self.assertIsNone(inverse_kinematics(0.0, 0.0, self.geometry))   # sur l'axe moteur


if __name__ == "__main__":
    unittest.main(verbosity=2)
