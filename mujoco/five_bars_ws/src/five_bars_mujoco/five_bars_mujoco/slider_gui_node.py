#!/usr/bin/env python3
"""ÉTAPE 3 — IHM à curseurs (q1, q4) publiant sur le topic de commande.

    ros2 run five_bars_mujoco slider_gui

C'est l'interface directe de l'étape 1, mais au lieu d'écrire dans MuJoCo elle
publie [q1, q4] (std_msgs/Float64MultiArray) sur ~command_topic, le topic lu par
five_bars_sim_node et sur lequel publie aussi le hardware interface ros2_control.

Pour piloter VIA ros2_control (forward_position_controller), il suffit de changer
le topic : -p command_topic:=/forward_position_controller/commands (même type).

Les curseurs ne publient que lorsqu'on les bouge : l'IHM et ros2_control peuvent
donc cohabiter sur le même topic. Les mesures (q1, q4) sont lues sur ~state_topic.
"""
from __future__ import annotations

import math
import tkinter as tk

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray

from five_bars_mujoco import topics
from five_bars_mujoco.slider_panel import SliderPanel

# Débattements par défaut (rad) — identiques à config/geometry.yaml
DEFAULT_RANGES = {"q1": (0.5236, 2.9671), "q4": (0.1745, 2.6180)}
DEFAULT_HOME = {"q1": 1.5707963, "q4": 1.1504938}


class SliderGuiNode(Node):
    def __init__(self):
        super().__init__("five_bars_slider_gui")
        self.declare_parameter("command_topic", topics.COMMAND_TOPIC)
        self.declare_parameter("state_topic", topics.SIM_ACTUATED_STATE_TOPIC)
        self.declare_parameter("q1_range", list(DEFAULT_RANGES["q1"]))
        self.declare_parameter("q4_range", list(DEFAULT_RANGES["q4"]))
        p = lambda n: self.get_parameter(n).value  # noqa: E731
        self.ranges = {"q1": tuple(p("q1_range")), "q4": tuple(p("q4_range"))}
        self.pub = self.create_publisher(Float64MultiArray, p("command_topic"), 10)
        self.sub = self.create_subscription(JointState, p("state_topic"), self.on_state, 10)
        self.measured: dict[str, float] = {}
        self.got_first_state = False
        self.get_logger().info(f"Publication des consignes sur '{p('command_topic')}'")

    def publish(self, q1: float, q4: float) -> None:
        self.pub.publish(Float64MultiArray(data=[float(q1), float(q4)]))

    def on_state(self, msg: JointState) -> None:
        self.measured.update(zip(msg.name, msg.position))


def main(args=None):
    rclpy.init(args=args)
    node = SliderGuiNode()
    root = tk.Tk()
    root.title("Système 5 barres — consignes via topic")
    panel = SliderPanel(root, node.ranges, DEFAULT_HOME, on_change=node.publish)
    panel.pack(fill="both", expand=True)

    def tick():
        rclpy.spin_once(node, timeout_sec=0.0)
        m = node.measured
        if "joint_q1" in m and "joint_q4" in m:
            if not node.got_first_state:
                # Initialise les curseurs sur la position mesurée, sans publier.
                panel.set_values_rad(m["joint_q1"], m["joint_q4"])
                node.got_first_state = True
            panel.status.set(f"mesure  q1 = {math.degrees(m['joint_q1']):7.2f}°   "
                             f"q4 = {math.degrees(m['joint_q4']):7.2f}°")
        else:
            panel.status.set("en attente des états du simulateur...")
        if rclpy.ok():
            root.after(10, tick)
        else:
            root.destroy()

    root.after(10, tick)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
