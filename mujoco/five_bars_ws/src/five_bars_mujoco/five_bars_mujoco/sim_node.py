#!/usr/bin/env python3
"""ÉTAPE 3 — Simulateur MuJoCo du 5 barres piloté par topic.

    ros2 run five_bars_mujoco sim_node [--ros-args -p use_viewer:=false]

Abonnement :
  ~command_topic (std_msgs/Float64MultiArray, data = [q1, q4] en rad, angles absolus)
      -> c'est aussi le topic sur lequel publie le hardware interface ros2_control.
Publications (à publish_rate Hz) :
  ~state_topic       (sensor_msgs/JointState) : joint_q1, joint_q4 (position, vitesse, effort)
  ~full_state_topic  (sensor_msgs/JointState) : toutes les liaisons (vérité terrain simulée)
  ~pen_topic         (geometry_msgs/PointStamped) : pointe du stylo dans le repère 'base'
Service :
  ~/reset (std_srvs/Trigger) : retour à la configuration 'home'.
"""
from __future__ import annotations

import math
import time

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
from std_srvs.srv import Trigger

from five_bars_mujoco import topics
from five_bars_mujoco.sim import ACTUATED_JOINTS, ALL_JOINTS, FiveBarsSim, configure_viewer_camera


class FiveBarsSimNode(Node):
    def __init__(self):
        super().__init__("five_bars_sim")
        self.declare_parameter("model_path", "")
        self.declare_parameter("use_viewer", True)
        self.declare_parameter("publish_rate", 200.0)
        self.declare_parameter("real_time_factor", 1.0)
        self.declare_parameter("max_speed", FiveBarsSim.DEFAULT_MAX_SPEED)
        self.declare_parameter("command_topic", topics.COMMAND_TOPIC)
        self.declare_parameter("state_topic", topics.SIM_ACTUATED_STATE_TOPIC)
        self.declare_parameter("full_state_topic", topics.SIM_FULL_STATE_TOPIC)
        self.declare_parameter("pen_topic", topics.SIM_PEN_TOPIC)
        p = lambda n: self.get_parameter(n).value  # noqa: E731

        max_speed = p("max_speed")
        self.sim = FiveBarsSim(p("model_path") or None, max_speed=max_speed if max_speed > 0 else None)
        self.get_logger().info(f"Modèle MuJoCo : {self.sim.model_path}")
        self.rtf = float(p("real_time_factor"))

        self.viewer = None
        if p("use_viewer"):
            try:
                import mujoco.viewer

                self.viewer = mujoco.viewer.launch_passive(self.sim.model, self.sim.data)
                configure_viewer_camera(self.viewer.cam)
            except Exception as exc:  # pas d'affichage disponible
                self.get_logger().warn(f"Viewer MuJoCo indisponible ({exc}) : simulation headless.")

        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self.cmd_sub = self.create_subscription(Float64MultiArray, p("command_topic"), self.on_command, qos)
        self.state_pub = self.create_publisher(JointState, p("state_topic"), qos)
        self.full_pub = self.create_publisher(JointState, p("full_state_topic"), qos)
        self.pen_pub = self.create_publisher(PointStamped, p("pen_topic"), qos)
        self.reset_srv = self.create_service(Trigger, "~/reset", self.on_reset)

        self._wall0 = time.perf_counter()
        self._sim0 = self.sim.time
        self.timer = self.create_timer(1.0 / float(p("publish_rate")), self.on_timer)
        self.get_logger().info(
            f"Simulation prête : commandes sur '{p('command_topic')}', états sur '{p('state_topic')}'.")

    # ---------------------------------------------------------------- callbacks
    def on_command(self, msg: Float64MultiArray) -> None:
        if len(msg.data) != 2 or not all(math.isfinite(v) for v in msg.data):
            self.get_logger().warn(
                f"Commande ignorée : attendu data=[q1, q4] finis, reçu {list(msg.data)}",
                throttle_duration_sec=1.0)
            return
        q1, q4 = self.sim.set_command(msg.data[0], msg.data[1])
        if abs(q1 - msg.data[0]) > 1e-9 or abs(q4 - msg.data[1]) > 1e-9:
            self.get_logger().warn("Commande saturée aux débattements des servos.", throttle_duration_sec=1.0)

    def on_reset(self, _req, resp):
        self._lock_and(self.sim.reset)
        self._wall0, self._sim0 = time.perf_counter(), self.sim.time
        resp.success, resp.message = True, "Simulation remise en configuration home"
        return resp

    def _lock_and(self, fn, *args):
        if self.viewer is not None:
            with self.viewer.lock():
                return fn(*args)
        return fn(*args)

    def on_timer(self) -> None:
        # Avance en temps réel (× real_time_factor), sans dériver.
        target = self._sim0 + self.rtf * (time.perf_counter() - self._wall0)
        n = int((target - self.sim.time) / self.sim.timestep)
        if n > 2000:  # retard trop important (pause, débogueur...) : on recale
            self._wall0, self._sim0 = time.perf_counter(), self.sim.time
            n = 1
        self._lock_and(self.sim.step, max(n, 0))
        if self.viewer is not None:
            if not self.viewer.is_running():
                self.get_logger().info("Viewer fermé : arrêt du simulateur.")
                raise SystemExit
            self.viewer.sync()
        self.publish_states()

    def publish_states(self) -> None:
        stamp = self.get_clock().now().to_msg()
        q, dq, tau = (self.sim.actuated_positions(), self.sim.actuated_velocities(),
                      self.sim.actuated_efforts())
        msg = JointState()
        msg.header.stamp = stamp
        msg.name = list(ACTUATED_JOINTS)
        msg.position, msg.velocity, msg.effort = q.tolist(), dq.tolist(), tau.tolist()
        self.state_pub.publish(msg)

        full = JointState()
        full.header.stamp = stamp
        full.name = list(ALL_JOINTS)
        pos, vel = self.sim.joint_positions(), self.sim.joint_velocities()
        full.position = [pos[j] for j in ALL_JOINTS]
        full.velocity = [vel[j] for j in ALL_JOINTS]
        self.full_pub.publish(full)

        pen = PointStamped()
        pen.header.stamp = stamp
        pen.header.frame_id = topics.BASE_FRAME
        pen.point.x, pen.point.y, pen.point.z = self.sim.pen_position().tolist()
        self.pen_pub.publish(pen)

    def destroy_node(self):
        if self.viewer is not None:
            self.viewer.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = FiveBarsSimNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
