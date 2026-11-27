#!/usr/bin/env python3
"""Mesure la géométrie du système 5 barres à partir des maillages COLLADA du cours.

Les fichiers base.dae, link1.dae ... link4.dae (exportés de maquette-5-barres_asm.stp
avec FreeCAD) sont exprimés dans le repère de l'assemblage CAO :
    x_cad horizontal, y_cad vertical (axe des pivots), z_cad horizontal.
On ajuste des cercles (moindres carrés) sur les sommets des alésages des liaisons
pour retrouver les centres A1..A5 et l'alésage Ø12 du porte-stylo.

Passage CAO -> R0 (schéma cinématique) :
    X0 = x_cad - x_A1,   Y0 = z_A1 - z_cad,   Z0 = y_cad
(R0 est direct : x0 ^ y0 = z0 vers le haut).

Usage : python3 measure_cad.py <dossier_contenant_les_dae>
"""
import sys
import numpy as np
import trimesh

# (pièce, centre approximatif (x_cad, z_cad) en mm, rayon de l'alésage en mm)
FEATURES = {
    "A1": ("link1", (-80.0, 70.0), 8.0),
    "A2": ("link2", (-80.0, -10.0), 11.0),
    "A3": ("link3", (19.9, -131.2), 11.0),
    "A4": ("link3", (90.2, -2.2), 11.0),
    "A5": ("link4", (58.0, 70.0), 8.0),
    "PEN": ("link2", (-6.5, -132.2), 6.0),
}


def fit_circle(p):
    a = np.c_[2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))]
    b = (p ** 2).sum(1)
    c, *_ = np.linalg.lstsq(a, b, rcond=None)
    return c[:2], np.sqrt(c[2] + c[0] ** 2 + c[1] ** 2)


def measure(dae_dir):
    pts = {}
    centers = {}
    for name, (part, guess, r0) in FEATURES.items():
        if part not in pts:
            m = trimesh.load(f"{dae_dir}/{part}.dae", force="scene").to_geometry()
            pts[part] = np.unique(np.round(m.vertices[:, [0, 2]] * 1000.0, 4), axis=0)
        p = pts[part]
        sel = p[np.abs(np.linalg.norm(p - np.array(guess), axis=1) - r0) < 0.6]
        c, r = fit_circle(sel)
        for _ in range(3):
            sel = p[np.abs(np.linalg.norm(p - c, axis=1) - r) < 0.05]
            c, r = fit_circle(sel)
        centers[name] = c
    a1 = centers["A1"]
    to_r0 = lambda c: np.array([c[0] - a1[0], a1[1] - c[1]]) / 1000.0  # noqa: E731
    A = {k: to_r0(v) for k, v in centers.items()}
    l0 = np.linalg.norm(A["A5"] - A["A1"])
    l1 = np.linalg.norm(A["A2"] - A["A1"])
    l2 = np.linalg.norm(A["A3"] - A["A2"])
    l3 = np.linalg.norm(A["A3"] - A["A4"])
    l4 = np.linalg.norm(A["A4"] - A["A5"])
    u = (A["A3"] - A["A2"]) / l2
    n = np.array([-u[1], u[0]])
    d = A["PEN"] - A["A3"]
    q1 = np.arctan2(*(A["A2"] - A["A1"])[::-1])
    q4 = np.arctan2(*(A["A4"] - A["A5"])[::-1])
    return dict(A=A, a1_cad=a1 / 1000.0, l0=l0, l1=l1, l2=l2, l3=l3, l4=l4,
                pen_dx=d @ u, pen_dy=d @ n, q1=q1, q4=q4)


if __name__ == "__main__":
    res = measure(sys.argv[1] if len(sys.argv) > 1 else ".")
    for k, v in res["A"].items():
        print(f"{k:4s} (R0) = ({v[0]*1000:9.3f}, {v[1]*1000:9.3f}) mm")
    for k in ["l0", "l1", "l2", "l3", "l4", "pen_dx", "pen_dy"]:
        print(f"{k:7s}= {res[k]:.6f} m")
    print(f"q1_ref = {res['q1']:.7f} rad ({np.degrees(res['q1']):.2f} deg)")
    print(f"q4_ref = {res['q4']:.7f} rad ({np.degrees(res['q4']):.2f} deg)")
