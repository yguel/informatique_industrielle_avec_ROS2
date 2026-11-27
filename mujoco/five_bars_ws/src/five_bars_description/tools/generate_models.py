#!/usr/bin/env python3
"""Génère le modèle MuJoCo (MJCF) du système 5 barres à partir de config/geometry.yaml.

    python3 tools/generate_models.py            # écrit mjcf/five_bars.xml

L'URDF (urdf/five_bars.urdf.xacro) lit directement geometry.yaml via xacro,
il n'a donc pas besoin d'être régénéré.

Structure de l'arbre cinématique MuJoCo (la boucle est fermée par une contrainte) :

    world (bâti, repère R0, origine A1)
    ├── link1  joint_q1 (pivot A1, ACTIF,   angle absolu q1)
    │   └── link2  joint_A2 (pivot A2, passif, angle relatif)  [site A3_link2, site pen_tip]
    └── link4  joint_q4 (pivot A5, ACTIF,   angle absolu q4)
        └── link3  joint_A4 (pivot A4, passif, angle relatif)  [site A3_link3]
    equality/connect : A3_link2 == A3_link3   (fermeture de la chaîne en A3)

Chaque bras a son repère local : origine sur le pivot proximal, x le long du bras.
Avec cette convention, la valeur de joint_q1 (resp. joint_q4) EST l'angle absolu q1
(resp. q4) du schéma cinématique.
"""
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)

TEMPLATE = """<?xml version="1.0"?>
<!-- FICHIER GÉNÉRÉ par tools/generate_models.py à partir de config/geometry.yaml : ne pas éditer à la main. -->
<mujoco model="five_bars">
  <compiler angle="radian" meshdir="../meshes" autolimits="true"/>
  <option timestep="0.001" integrator="implicitfast"/>

  <visual>
    <global offwidth="1280" offheight="960" azimuth="90" elevation="-89"/>
    <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3"/>
  </visual>

  <default>
    <joint type="hinge" axis="0 0 1" damping="0.002" armature="0.0005"/>
    <geom contype="0" conaffinity="0"/>
    <site size="0.003" rgba="1 0.2 0.2 1"/>
    <default class="visual">
      <geom type="mesh" group="2" mass="0"/>
    </default>
    <default class="servo">
      <!-- Dynamixel AX-12A : couple de blocage ~1.5 N.m -->
      <position kp="8" kv="0.16" forcerange="-1.5 1.5"/>
    </default>
  </default>

  <asset>
    <material name="frame" rgba="0.75 0.75 0.78 1"/>
    <material name="arm" rgba="0.15 0.15 0.15 1"/>
    <material name="arm_left" rgba="0.2 0.6 0.25 1"/>
    <material name="arm_right" rgba="0.2 0.35 0.75 1"/>
    <material name="pen" rgba="0.8 0.1 0.1 1"/>
    <mesh name="base" file="base.stl"/>
    <mesh name="link1" file="link1.stl"/>
    <mesh name="link2" file="link2.stl"/>
    <mesh name="link3" file="link3.stl"/>
    <mesh name="link4" file="link4.stl"/>
  </asset>

  <worldbody>
    <light pos="0.07 0.1 0.8" dir="0 0 -1" directional="true"/>
    <camera name="top" pos="{cx} {cy} 0.65" xyaxes="1 0 0 0 1 0"/>
    <geom name="base" class="visual" mesh="base" material="frame"/>
    <site name="A1" pos="0 0 {jz}"/>
    <site name="A5" pos="{l0} 0 {jz}"/>

    <body name="link1">
      <inertial pos="{l1h} 0 {jz}" mass="0.030" diaginertia="2e-6 2e-5 2e-5"/>
      <joint name="joint_q1" range="{q1min} {q1max}"/>
      <geom class="visual" mesh="link1" material="arm_left"/>
      <site name="A2" pos="{l1} 0 {jz}"/>
      <body name="link2" pos="{l1} 0 0">
        <inertial pos="{l2h} 0 {jz}" mass="0.040" diaginertia="3e-6 8e-5 8e-5"/>
        <joint name="joint_A2"/>
        <geom class="visual" mesh="link2" material="arm_left"/>
        <site name="A3_link2" pos="{l2} 0 {jz}"/>
        <site name="pen_tip" pos="{penx} {peny} {penz}" size="0.004" rgba="1 0 0 1"/>
        <geom name="pen" type="cylinder" size="0.005 0.035" pos="{penx} {peny} {pencz}" material="pen" group="1" mass="0"/>
      </body>
    </body>

    <body name="link4" pos="{l0} 0 0">
      <inertial pos="{l4h} 0 {jz}" mass="0.030" diaginertia="2e-6 2e-5 2e-5"/>
      <joint name="joint_q4" range="{q4min} {q4max}"/>
      <geom class="visual" mesh="link4" material="arm_right"/>
      <site name="A4" pos="{l4} 0 {jz}"/>
      <body name="link3" pos="{l4} 0 0">
        <inertial pos="{l3h} 0 {jz}" mass="0.035" diaginertia="3e-6 7e-5 7e-5"/>
        <joint name="joint_A4"/>
        <geom class="visual" mesh="link3" material="arm_right"/>
        <site name="A3_link3" pos="{l3} 0 {jz}"/>
      </body>
    </body>
  </worldbody>

  <equality>
    <!-- Fermeture de la chaîne cinématique : les deux avant-bras partagent le pivot A3 -->
    <connect name="closure_A3" site1="A3_link2" site2="A3_link3" solref="0.004 1"/>
  </equality>

  <actuator>
    <position name="act_q1" class="servo" joint="joint_q1" ctrlrange="{q1min} {q1max}"/>
    <position name="act_q4" class="servo" joint="joint_q4" ctrlrange="{q4min} {q4max}"/>
  </actuator>

  <sensor>
    <jointpos name="q1" joint="joint_q1"/>
    <jointpos name="q4" joint="joint_q4"/>
    <jointvel name="dq1" joint="joint_q1"/>
    <jointvel name="dq4" joint="joint_q4"/>
    <framepos name="pen_pos" objtype="site" objname="pen_tip"/>
  </sensor>

  <keyframe>
    <!-- Configuration de l'assemblage CAO (qpos = joint_q1, joint_A2, joint_q4, joint_A4) -->
    <key name="home" qpos="{q1ref} {a2ref} {q4ref} {a4ref}" ctrl="{q1ref} {q4ref}"/>
  </keyframe>
</mujoco>
"""


def main():
    with open(os.path.join(PKG, "config", "geometry.yaml")) as f:
        cfg = yaml.safe_load(f)
    g, ref, lim = cfg["geometry"], cfg["reference_configuration"], cfg["limits"]
    jz = 0.085  # hauteur des sites de pivots (cosmétique)
    fmt = lambda v: f"{v:.6f}"  # noqa: E731
    values = dict(
        l0=fmt(g["l0"]), l1=fmt(g["l1"]), l2=fmt(g["l2"]), l3=fmt(g["l3"]), l4=fmt(g["l4"]),
        l1h=fmt(g["l1"] / 2), l2h=fmt(g["l2"] / 2), l3h=fmt(g["l3"] / 2), l4h=fmt(g["l4"] / 2),
        penx=fmt(g["l2"] + g["pen_dx"]), peny=fmt(g["pen_dy"]), penz=fmt(g["pen_z"]),
        pencz=fmt(g["pen_z"] + 0.035), jz=fmt(jz),
        q1min=fmt(lim["q1"][0]), q1max=fmt(lim["q1"][1]),
        q4min=fmt(lim["q4"][0]), q4max=fmt(lim["q4"][1]),
        q1ref=fmt(ref["q1"]), q4ref=fmt(ref["q4"]),
        a2ref=fmt(ref["joint_A2"]), a4ref=fmt(ref["joint_A4"]),
        cx=fmt(g["l0"] / 2), cy=fmt(0.11),
    )
    out = os.path.join(PKG, "mjcf", "five_bars.xml")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(TEMPLATE.format(**values))
    print(f"MJCF écrit : {out}")


if __name__ == "__main__":
    main()
