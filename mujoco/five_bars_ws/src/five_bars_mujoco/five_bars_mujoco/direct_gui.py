#!/usr/bin/env python3
"""ÉTAPE 1 — Interface graphique directe (sans ROS) : réglage de q1 et q4 dans MuJoCo.

    python3 -m five_bars_mujoco.direct_gui [--model chemin/five_bars.xml] [--no-viewer]
    # ou, une fois le workspace compilé :
    ros2 run five_bars_mujoco direct_gui

Une fenêtre Tk avec deux curseurs (q1, q4) pilote directement les consignes des
actionneurs de position MuJoCo ; la scène 3D s'affiche dans le viewer MuJoCo.
La simulation est cadencée en temps réel par la boucle Tk (after()).
"""
from __future__ import annotations

import argparse
import math
import time
import tkinter as tk

import mujoco
import mujoco.viewer

from five_bars_mujoco.sim import FiveBarsSim, configure_viewer_camera
from five_bars_mujoco.slider_panel import SliderPanel

GUI_PERIOD_MS = 10  # 100 Hz


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default=None, help="chemin du MJCF (défaut : five_bars_description)")
    parser.add_argument("--no-viewer", action="store_true", help="pas de viewer 3D (curseurs seuls)")
    args, _ = parser.parse_known_args(argv)

    sim = FiveBarsSim(args.model)
    viewer = None
    if not args.no_viewer:
        viewer = mujoco.viewer.launch_passive(sim.model, sim.data)
        configure_viewer_camera(viewer.cam)

    root = tk.Tk()
    root.title("Système 5 barres — commande directe MuJoCo")
    q0 = sim.actuated_positions()
    panel = SliderPanel(
        root,
        ranges_rad={"q1": sim.ctrl_range("joint_q1"), "q4": sim.ctrl_range("joint_q4")},
        initial_rad={"q1": q0[0], "q4": q0[1]},
        on_change=lambda q1, q4: sim.set_command(q1, q4),
    )
    panel.pack(fill="both", expand=True)

    wall_start = time.perf_counter()
    sim_start = sim.time

    def tick():
        # Simulation en temps réel : on rattrape le temps mur écoulé.
        target = sim_start + (time.perf_counter() - wall_start)
        n = max(0, int((target - sim.time) / sim.timestep))
        if viewer is not None:
            with viewer.lock():
                sim.step(n)
            viewer.sync()
            if not viewer.is_running():
                root.destroy()
                return
        else:
            sim.step(n)
        q = sim.actuated_positions()
        joints = sim.joint_positions()
        pen = sim.pen_position()
        panel.status.set(
            f"mesure  q1 = {math.degrees(q[0]):7.2f}°   q4 = {math.degrees(q[1]):7.2f}°\n"
            f"passifs A2 = {math.degrees(joints['joint_A2']):7.2f}°   A4 = {math.degrees(joints['joint_A4']):7.2f}°\n"
            f"stylo   x = {pen[0]*1000:7.2f} mm   y = {pen[1]*1000:7.2f} mm\n"
            f"fermeture |A3_2 - A3_3| = {sim.closure_error()*1e6:6.2f} µm   t = {sim.time:7.2f} s"
        )
        root.after(GUI_PERIOD_MS, tick)

    root.after(GUI_PERIOD_MS, tick)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    try:
        root.mainloop()
    finally:
        if viewer is not None:
            viewer.close()


if __name__ == "__main__":
    main()
