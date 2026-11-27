#!/usr/bin/env python3
"""ÉTAPE 4 — Mise à jour de l'état complet d'une chaîne cinématique fermée avec MuJoCo.

    ros2 run five_bars_mujoco state_updater [--ros-args -p input_topic:=...]

Seuls q1 et q4 sont mesurés (servos). Les pivots passifs A2 et A4 ne le sont pas,
or robot_state_publisher a besoin de TOUTES les liaisons de l'URDF pour publier
les TF (et donc afficher link2, link3 et le stylo dans RViz).

Ce nœud :
  1. reçoit (q1, q4) sur ~input_topic (sensor_msgs/JointState), par défaut la sortie
     du joint_state_broadcaster de ros2_control ;
  2. impose q1, q4 dans SA PROPRE instance du modèle MuJoCo et résout la fermeture
     de chaîne en A3 (Newton sur les angles passifs, jacobiennes MuJoCo), en partant
     de la solution précédente : on reste ainsi sur la même branche d'assemblage ;
  3. calcule les vitesses passives (dq_p = -J_p^+ J_a dq_a) ;
  4. publie l'état complet sur ~output_topic (/joint_states) et la position du stylo.

Il fonctionne aussi bien avec la simulation qu'avec le vrai robot (Dynamixel).
"""
from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from sensor_msgs.msg import JointState

from five_bars_mujoco import topics
from five_bars_mujoco.sim import ALL_JOINTS, FiveBarsSim


class StateUpdaterNode(Node):
    def __init__(self):
        super().__init__("five_bars_state_updater")
        self.declare_parameter("model_path", "")
        self.declare_parameter("input_topic", topics.JSB_STATE_TOPIC)
        self.declare_parameter("output_topic", topics.FULL_JOINT_STATES_TOPIC)
        self.declare_parameter("pen_topic", topics.PEN_TOPIC)
        self.declare_parameter("tolerance", 1e-9)
        p = lambda n: self.get_parameter(n).value  # noqa: E731

        # Modèle utilisé uniquement en cinématique (pas de mj_step).
        self.model = FiveBarsSim(p("model_path") or None)
        self.tol = float(p("tolerance"))
        self.pub = self.create_publisher(JointState, p("output_topic"), 10)
        self.pen_pub = self.create_publisher(PointStamped, p("pen_topic"), 10)
        self.sub = self.create_subscription(JointState, p("input_topic"), self.on_joint_state, 10)
        self._last_good = self.model.data.qpos.copy()
        self.get_logger().info(f"État complet : '{p('input_topic')}' (q1, q4) -> '{p('output_topic')}'")

    def on_joint_state(self, msg: JointState) -> None:
        idx = {n: i for i, n in enumerate(msg.name)}
        if "joint_q1" not in idx or "joint_q4" not in idx:
            return
        q1, q4 = msg.position[idx["joint_q1"]], msg.position[idx["joint_q4"]]
        if not (math.isfinite(q1) and math.isfinite(q4)):
            return
        ok = self.model.solve_closure(q1, q4, tol=self.tol)
        if not ok:
            # (q1, q4) hors de l'espace atteignable (ou singularité) : on garde le dernier état valide.
            self.model.data.qpos[:] = self._last_good
            self.model.solve_closure()
            self.get_logger().warn(
                f"Fermeture impossible pour q1={math.degrees(q1):.1f}°, q4={math.degrees(q4):.1f}° "
                "(hors espace de travail ?)", throttle_duration_sec=1.0)
            return
        self._last_good[:] = self.model.data.qpos

        has_vel = len(msg.velocity) == len(msg.name)
        dq1 = msg.velocity[idx["joint_q1"]] if has_vel else 0.0
        dq4 = msg.velocity[idx["joint_q4"]] if has_vel else 0.0
        dqa2, dqa4 = self.model.closure_velocities(dq1, dq4)
        vel = {"joint_q1": dq1, "joint_A2": dqa2, "joint_q4": dq4, "joint_A4": dqa4}

        pos = self.model.joint_positions()
        out = JointState()
        out.header.stamp = msg.header.stamp if msg.header.stamp.sec or msg.header.stamp.nanosec \
            else self.get_clock().now().to_msg()
        out.name = list(ALL_JOINTS)
        out.position = [pos[j] for j in ALL_JOINTS]
        out.velocity = [vel[j] for j in ALL_JOINTS]
        self.pub.publish(out)

        pen = PointStamped()
        pen.header.stamp = out.header.stamp
        pen.header.frame_id = topics.BASE_FRAME
        pen.point.x, pen.point.y, pen.point.z = self.model.pen_position().tolist()
        self.pen_pub.publish(pen)


def main(args=None):
    rclpy.init(args=args)
    node = StateUpdaterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
