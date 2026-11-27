"""Simulation MuJoCo du système 5 barres (sans dépendance ROS).

Conventions (voir five_bars_description/config/geometry.yaml) :
  * repère R0 : origine A1, x0 vers A5, z0 vers le haut ;
  * q1 = valeur de joint_q1 = angle ABSOLU du bras gauche (A1A2) par rapport à x0 ;
  * q4 = valeur de joint_q4 = angle ABSOLU du bras droit  (A5A4) par rapport à x0 ;
  * joint_A2, joint_A4 : pivots passifs (angles relatifs) ;
  * la boucle est fermée en A3 par une contrainte d'égalité MuJoCo (connect).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import mujoco
import numpy as np

ACTUATED_JOINTS = ("joint_q1", "joint_q4")
PASSIVE_JOINTS = ("joint_A2", "joint_A4")
ALL_JOINTS = ("joint_q1", "joint_A2", "joint_q4", "joint_A4")


def default_model_path() -> str:
    """Chemin du MJCF : $FIVE_BARS_MJCF, sinon le paquet ROS installé, sinon l'arbre source."""
    env = os.environ.get("FIVE_BARS_MJCF")
    if env:
        return env
    try:
        from ament_index_python.packages import get_package_share_directory

        return os.path.join(get_package_share_directory("five_bars_description"), "mjcf", "five_bars.xml")
    except Exception:  # pas de ROS ou paquet non installé
        here = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(here, "..", "..", "five_bars_description", "mjcf", "five_bars.xml"))


def configure_viewer_camera(cam) -> None:
    """Cadre la caméra libre du viewer MuJoCo sur le mécanisme (vue de dessus inclinée)."""
    cam.lookat[:] = (0.07, 0.10, 0.05)
    cam.distance = 0.50
    cam.azimuth = 90.0
    cam.elevation = -65.0


@dataclass
class FiveBarsGeometry:
    """Paramètres géométriques (m) extraits du modèle MuJoCo — source de vérité des tests."""

    l0: float
    l1: float
    l2: float
    l3: float
    l4: float
    pen_dx: float  # décalage du stylo / A3, le long de A2->A3
    pen_dy: float  # décalage du stylo / A3, perpendiculaire (à gauche de A2->A3)

    @classmethod
    def from_model(cls, model: mujoco.MjModel) -> "FiveBarsGeometry":
        body = lambda n: model.body(n).pos  # noqa: E731
        site = lambda n: model.site(n).pos  # noqa: E731
        l2 = float(site("A3_link2")[0])
        return cls(
            l0=float(body("link4")[0] - body("link1")[0]),
            l1=float(body("link2")[0]),
            l2=l2,
            l3=float(site("A3_link3")[0]),
            l4=float(body("link3")[0]),
            pen_dx=float(site("pen_tip")[0] - l2),
            pen_dy=float(site("pen_tip")[1]),
        )


class FiveBarsSim:
    """Encapsule un modèle MuJoCo du 5 barres : commande (q1, q4), pas de simulation, états."""

    #: vitesse maximale des servos (rad/s) — AX-12A à vide : 59 tr/min ≈ 6.2 rad/s
    DEFAULT_MAX_SPEED = 6.0

    def __init__(self, model_path: str | None = None, max_speed: float | None = DEFAULT_MAX_SPEED):
        """max_speed : limitation de vitesse de la consigne (rad/s), None pour un échelon brut."""
        self.max_speed = max_speed
        self.model_path = model_path or default_model_path()
        self.model = mujoco.MjModel.from_xml_path(self.model_path)
        self.data = mujoco.MjData(self.model)
        m = self.model
        self._qadr = {j: int(m.jnt_qposadr[m.joint(j).id]) for j in ALL_JOINTS}
        self._dadr = {j: int(m.jnt_dofadr[m.joint(j).id]) for j in ALL_JOINTS}
        self._act = [m.actuator("act_q1").id, m.actuator("act_q4").id]
        self._pen = m.site("pen_tip").id
        self._s2 = m.site("A3_link2").id
        self._s3 = m.site("A3_link3").id
        self.geometry = FiveBarsGeometry.from_model(m)
        self.reset()

    # ------------------------------------------------------------------ état
    def reset(self) -> None:
        """Remet la simulation dans la configuration 'home' (assemblage CAO), chaîne refermée."""
        mujoco.mj_resetDataKeyframe(self.model, self.data, self.model.key("home").id)
        self.solve_closure()
        self._target = self.actuated_positions()
        self.data.ctrl[self._act] = self._target
        mujoco.mj_forward(self.model, self.data)

    @property
    def time(self) -> float:
        return float(self.data.time)

    @property
    def timestep(self) -> float:
        return float(self.model.opt.timestep)

    def ctrl_range(self, joint: str) -> tuple[float, float]:
        a = self._act[ACTUATED_JOINTS.index(joint)]
        lo, hi = self.model.actuator_ctrlrange[a]
        return float(lo), float(hi)

    def actuated_positions(self) -> np.ndarray:
        return np.array([self.data.qpos[self._qadr[j]] for j in ACTUATED_JOINTS])

    def actuated_velocities(self) -> np.ndarray:
        return np.array([self.data.qvel[self._dadr[j]] for j in ACTUATED_JOINTS])

    def actuated_efforts(self) -> np.ndarray:
        return np.array(self.data.actuator_force[self._act])

    def joint_positions(self) -> dict[str, float]:
        return {j: float(self.data.qpos[self._qadr[j]]) for j in ALL_JOINTS}

    def joint_velocities(self) -> dict[str, float]:
        return {j: float(self.data.qvel[self._dadr[j]]) for j in ALL_JOINTS}

    def pen_position(self) -> np.ndarray:
        """Position (x, y, z) de la pointe du stylo dans R0 (m)."""
        return self.data.site_xpos[self._pen].copy()

    def closure_error(self) -> float:
        return float(np.linalg.norm(self.data.site_xpos[self._s2] - self.data.site_xpos[self._s3]))

    # ------------------------------------------------------------ commande
    def set_command(self, q1: float, q4: float) -> tuple[float, float]:
        """Consigne de position des deux servos (rad, angles absolus). Saturée aux débattements.

        La consigne effectivement appliquée aux actionneurs rejoint cette cible à
        ``max_speed`` rad/s au plus (comme le 'moving speed' d'un Dynamixel).
        """
        cmd = []
        for j, q in zip(ACTUATED_JOINTS, (q1, q4)):
            lo, hi = self.ctrl_range(j)
            cmd.append(float(np.clip(q, lo, hi)))
        self._target = np.array(cmd)
        if self.max_speed is None:
            self.data.ctrl[self._act] = self._target
        return cmd[0], cmd[1]

    def command(self) -> tuple[float, float]:
        """Dernière consigne demandée (cible)."""
        return float(self._target[0]), float(self._target[1])

    def step(self, n: int = 1) -> None:
        """Avance la simulation de n pas (en appliquant la limitation de vitesse de consigne)."""
        m, d = self.model, self.data
        if n <= 0:
            return
        if self.max_speed is None or np.array_equal(d.ctrl[self._act], self._target):
            mujoco.mj_step(m, d, nstep=n)
            return
        dmax = self.max_speed * m.opt.timestep
        for k in range(n):
            delta = self._target - d.ctrl[self._act]
            if not delta.any():
                mujoco.mj_step(m, d, nstep=n - k)
                return
            d.ctrl[self._act] += np.clip(delta, -dmax, dmax)
            mujoco.mj_step(m, d)

    def settle(self, q1: float, q4: float, ramp_time: float = 0.4, hold_time: float = 0.6,
               vel_tol: float = 1e-4, max_time: float = 5.0) -> bool:
        """Simulation (dynamique) jusqu'à l'équilibre sur la consigne (q1, q4).

        La consigne est interpolée linéairement pendant ``ramp_time`` pour suivre
        continûment la branche d'assemblage courante. Renvoie True si l'équilibre
        est atteint (vitesses < vel_tol rad/s).
        """
        q_start = np.array(self.command())
        q_goal = np.array([q1, q4])
        n_ramp = max(1, int(ramp_time / self.timestep))
        for k in range(1, n_ramp + 1):
            self.set_command(*(q_start + (q_goal - q_start) * k / n_ramp))
            self.step()
        self.step(int(hold_time / self.timestep))
        t_end = self.time + max_time
        while self.time < t_end:
            if np.max(np.abs(self.data.qvel)) < vel_tol:
                return True
            self.step(10)
        return False

    # ------------------------------------------------- fermeture cinématique
    def solve_closure(self, q1: float | None = None, q4: float | None = None,
                      tol: float = 1e-10, max_iter: int = 50) -> bool:
        """Résout la fermeture de chaîne : (q1, q4) imposés, calcule les pivots passifs.

        Méthode de Newton (moindres carrés) sur les angles passifs, en utilisant le
        modèle MuJoCo pour la cinématique des sites A3 (positions + jacobiennes).
        Part de la configuration courante (garde donc la branche d'assemblage).
        Modifie data.qpos et met les vitesses à zéro. Renvoie True si convergé.
        """
        m, d = self.model, self.data
        if q1 is not None:
            d.qpos[self._qadr["joint_q1"]] = q1
        if q4 is not None:
            d.qpos[self._qadr["joint_q4"]] = q4
        cols = [self._dadr[j] for j in PASSIVE_JOINTS]
        qcols = [self._qadr[j] for j in PASSIVE_JOINTS]
        jac2 = np.zeros((3, m.nv))
        jac3 = np.zeros((3, m.nv))
        ok = False
        for _ in range(max_iter):
            mujoco.mj_kinematics(m, d)
            mujoco.mj_comPos(m, d)
            err = d.site_xpos[self._s2] - d.site_xpos[self._s3]
            if np.linalg.norm(err) < tol:
                ok = True
                break
            mujoco.mj_jacSite(m, d, jac2, None, self._s2)
            mujoco.mj_jacSite(m, d, jac3, None, self._s3)
            j = (jac2 - jac3)[:2, cols]  # mécanisme plan : x, y
            dq, *_ = np.linalg.lstsq(j, -err[:2], rcond=None)
            d.qpos[qcols] += dq
        d.qvel[:] = 0.0
        mujoco.mj_forward(m, d)
        return ok

    def closure_velocities(self, dq1: float, dq4: float) -> tuple[float, float]:
        """Vitesses des pivots passifs (joint_A2, joint_A4) compatibles avec la fermeture.

        La contrainte de fermeture s'écrit J_a dq_a + J_p dq_p = 0 (vitesse relative
        nulle des sites A3), d'où dq_p = -J_p^+ J_a dq_a. À appeler après solve_closure().
        """
        m, d = self.model, self.data
        jac2 = np.zeros((3, m.nv))
        jac3 = np.zeros((3, m.nv))
        mujoco.mj_jacSite(m, d, jac2, None, self._s2)
        mujoco.mj_jacSite(m, d, jac3, None, self._s3)
        j = (jac2 - jac3)[:2]
        ja = j[:, [self._dadr[n] for n in ACTUATED_JOINTS]]
        jp = j[:, [self._dadr[n] for n in PASSIVE_JOINTS]]
        dqp, *_ = np.linalg.lstsq(jp, -ja @ np.array([dq1, dq4]), rcond=None)
        return float(dqp[0]), float(dqp[1])
