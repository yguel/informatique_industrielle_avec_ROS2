#!/usr/bin/env python3
"""Amène les maillages CAO du 5 barres dans le repère et l'unité attendus par le modèle.

Le modèle (MJCF et URDF) exige trois choses de chaque maillage de meshes/ :

  * l'unité **mètre** ;
  * le **repère local du corps** porteur : origine sur le pivot proximal, x le long
    du bras vers le pivot distal, z vers le haut. Le bâti, lui, est exprimé dans R0 ;
  * au plus **200 000 faces** par STL, limite du décodeur STL de MuJoCo.

Or la CAO fournit ses pièces dans le repère de l'**assemblage**, et les exports STL
sortent souvent en millimètres (le format STL ne porte aucune unité). Ce script fait
les deux corrections, et la décimation si on la demande.

Repère de l'assemblage CAO : x_cad et z_cad horizontaux, y_cad vertical (axe des
pivots). Repère R0 du schéma cinématique : origine en A1, x0 vers A5, z0 vers le haut.
Le passage de l'un à l'autre est assuré par cad_to_r0() :

    X0 = x_cad - x_A1        on ramène l'origine sur l'axe du moteur gauche
    Y0 = z_A1  - z_cad       z_cad devient y0, de signe opposé (repère direct)
    Z0 = y_cad               la verticale de la CAO devient la verticale de R0

Il n'y a **pas** de translation verticale : z0 = 0 reste le plan y_cad = 0 de la CAO,
c'est pourquoi les axes des moteurs sont à z = 85 mm dans le modèle et non à z = 0.

Exemples :

    # les cinq pièces, pleine résolution, depuis les .dae
    python3 convert_cad.py ../../../../cad/pentograph ../meshes

    # le bâti seul, depuis le nouveau base.stl (sans butées), décimé sous la limite
    python3 convert_cad.py ../../../../cad/pentograph ../meshes \
            --parts base --input-ext stl --faces 195000

    # les butées : juste millimètres -> mètres, sans changement de repère
    python3 convert_cad.py ../../../../cad/pentograph /tmp/out \
            --parts stopper_01,stopper_02 --units-only
"""
import argparse
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_cad import measure  # noqa: E402
from check_meshes import EXPECTED, TOL_M  # noqa: E402

#: Les cinq corps du modèle, dans l'ordre où ils apparaissent dans la chaîne.
#: C'est la liste traitée par défaut.
BODIES = ["base", "link1", "link2", "link3", "link4"]

#: Pièces rigidement fixées au bâti : leur repère de corps est donc R0, comme
#: celui du bâti. Elles ne sont pas converties par défaut (--parts pour les
#: demander), et ne figurent ni dans l'URDF ni dans le MJCF.
BASE_ATTACHED = ["stopper_01", "stopper_02"]

#: Cibles de décimation utilisées par --simplify (nombre de faces par corps).
TARGET_FACES = {"base": 40000, "link1": 8000, "link2": 10000, "link3": 10000, "link4": 8000}

#: MuJoCo refuse de charger un STL de plus de 200 000 faces (stl_decoder).
MUJOCO_MAX_FACES = 200_000

#: Au-delà de cette taille de boîte englobante, --input-units auto conclut
#: « millimètres » : aucune pièce de ce robot ne dépasse 0,4 m, et la plus petite
#: fait 4 mm, donc 10 sépare largement les deux hypothèses.
AUTO_MM_THRESHOLD = 10.0

#: Facteur appliqué aux sommets selon l'unité d'entrée.
UNIT_SCALE = {"m": 1.0, "mm": 0.001}


def rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])


def load_part(in_dir, name, ext):
    """Charge <name>.dae ou <name>.stl selon `ext` ('auto', 'dae' ou 'stl')."""
    candidates = {"dae": f"{name}.dae", "stl": f"{name}.stl"}
    order = ["dae", "stl"] if ext == "auto" else [ext]
    for kind in order:
        path = os.path.join(in_dir, candidates[kind])
        if os.path.exists(path):
            loaded = trimesh.load(path, force="scene")
            mesh = loaded.to_geometry() if hasattr(loaded, "to_geometry") else loaded
            return mesh, path
    raise FileNotFoundError(
        f"aucun fichier pour « {name} » dans {in_dir} "
        f"(cherché : {', '.join(candidates[k] for k in order)})")


def detect_units(mesh, requested):
    """Retourne ('m'|'mm', facteur). `requested` vaut 'auto', 'm' ou 'mm'.

    Le COLLADA porte son unité et trimesh la applique : un .dae arrive donc en
    mètres. Le STL n'en porte aucune : les nombres sont bruts, le plus souvent
    des millimètres. D'où la détection sur la taille de la boîte englobante.
    """
    if requested != "auto":
        return requested, UNIT_SCALE[requested]
    unit = "mm" if float(mesh.extents.max()) > AUTO_MM_THRESHOLD else "m"
    return unit, UNIT_SCALE[unit]


def body_frames(ref_dir):
    """Origine (x0, y0) et orientation de chaque corps, mesurées sur les .dae.

    Les points A1..A5 qui définissent R0 sont retrouvés en ajustant des cercles sur
    les alésages des liaisons : cela exige les COLLADA d'origine, et eux seuls.
    """
    missing = [f"{n}.dae" for n in BODIES[1:]
               if not os.path.exists(os.path.join(ref_dir, f"{n}.dae"))]
    if missing:
        raise SystemExit(
            f"Erreur : {', '.join(missing)} introuvable(s) dans « {ref_dir} ».\n"
            f"Les repères des corps sont mesurés sur les COLLADA d'origine (les points\n"
            f"A1..A5 sont retrouvés sur les alésages des liaisons), pas sur les STL.\n"
            f"Indiquez où ils sont avec --ref-dir, par exemple :\n"
            f"    --ref-dir ../../../../cad/pentograph\n"
            f"Ou, si cette pièce n'a pas de repère de corps à respecter, utilisez "
            f"--units-only.")
    geo = measure(ref_dir)
    A = geo["A"]
    angle = lambda a, b: np.arctan2(b[1] - a[1], b[0] - a[0])  # noqa: E731
    frames = {name: (np.zeros(2), 0.0) for name in BASE_ATTACHED}
    frames.update({
        "base": (np.zeros(2), 0.0),
        "link1": (A["A1"], angle(A["A1"], A["A2"])),
        "link2": (A["A2"], angle(A["A2"], A["A3"])),
        "link3": (A["A4"], angle(A["A4"], A["A3"])),
        "link4": (A["A5"], angle(A["A5"], A["A4"])),
    })
    return geo["a1_cad"], frames


def already_in_body_frame(name, mesh):
    """Vrai si le maillage est déjà dans le repère du corps (conversion déjà faite).

    La conversion n'est pas idempotente : l'appliquer deux fois déplacerait et
    ferait tourner la pièce une seconde fois. On le détecte ici.
    """
    exp = EXPECTED.get(name)
    if exp is None:
        return False
    got = tuple(mesh.bounds[0]) + tuple(mesh.bounds[1])
    return max(abs(g - e) for g, e in zip(got, exp)) <= TOL_M


def main(in_dir, out_dir, parts=None, ext="auto", units="auto",
         units_only=False, targets=None, ref_dir=None):
    parts = parts or BODIES
    os.makedirs(out_dir, exist_ok=True)

    # measure() a besoin des .dae ; on ne l'appelle que si un repère est à changer.
    a1_cad, frames = (None, {}) if units_only else body_frames(ref_dir or in_dir)

    status = 0
    for name in parts:
        mesh, src = load_part(in_dir, name, ext)
        n_in = len(mesh.faces)

        if not units_only and already_in_body_frame(name, mesh):
            print(f"{name:10s}: DEJA CONVERTI, rien à faire. Sa boîte englobante est "
                  f"celle attendue dans le repère « {name} » ; le reconvertir le "
                  f"déplacerait une seconde fois.", file=sys.stderr)
            status = 1
            continue

        unit, scale = detect_units(mesh, units)

        v = np.asarray(mesh.vertices, dtype=float) * scale
        if units_only:
            how = f"{unit} -> m, repère inchangé"
        else:
            if name not in frames:
                print(f"{name:10s}: IGNORE, « {name} » n'est pas un des cinq corps "
                      f"({', '.join(BODIES)}). Utilisez --units-only pour une pièce "
                      f"sans repère défini.", file=sys.stderr)
                status = 1
                continue
            origin, theta = frames[name]
            # CAO -> R0 : origine sur A1, y0 = -z_cad, z0 = y_cad
            v = np.c_[v[:, 0] - a1_cad[0], a1_cad[1] - v[:, 2], v[:, 1]]
            v[:, :2] -= origin          # origine sur le pivot proximal du corps
            v = v @ rot_z(-theta).T     # x le long du bras
            how = f"{unit} -> m, CAO -> repère {name} ({np.degrees(theta):.2f} deg)"

        mesh = trimesh.Trimesh(v, mesh.faces, process=True)
        if targets and name in targets and len(mesh.faces) > targets[name]:
            mesh = mesh.simplify_quadric_decimation(face_count=targets[name])

        out = os.path.join(out_dir, f"{name}.stl")
        mesh.export(out)
        n_out = len(mesh.faces)
        print(f"{name:10s}: {n_in:7d} -> {n_out:7d} faces, {how}, "
              f"{os.path.getsize(out) / 1e6:5.2f} Mo")
        print(f"            {src} -> {out}")
        if n_out > MUJOCO_MAX_FACES:
            status = 1
            print(f"            /!\\ {n_out} faces > {MUJOCO_MAX_FACES} : MuJoCo "
                  f"REFUSERA ce fichier. Relancez avec --faces "
                  f"{MUJOCO_MAX_FACES - 5000}.", file=sys.stderr)
    return status


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("in_dir", help="dossier des maillages CAO (.dae et/ou .stl)")
    ap.add_argument("out_dir", help="dossier de sortie des .stl (en général meshes/)")
    ap.add_argument("--parts", metavar="A,B",
                    help=f"pièces à traiter, séparées par des virgules "
                         f"(défaut : {','.join(BODIES)})")
    ap.add_argument("--ref-dir", metavar="DIR",
                    help="dossier des .dae servant à mesurer les repères des corps "
                         "(défaut : in_dir). À donner quand on convertit un STL rangé "
                         "ailleurs que dans le dossier CAO")
    ap.add_argument("--input-ext", choices=["auto", "dae", "stl"], default="auto",
                    help="format d'entrée ; auto prend le .dae s'il existe, sinon le .stl")
    ap.add_argument("--input-units", choices=["auto", "m", "mm"], default="auto",
                    help="unité des fichiers d'entrée ; auto déduit de la taille "
                         "de la pièce (> 10 unités = millimètres)")
    ap.add_argument("--units-only", action="store_true",
                    help="ne faire QUE la conversion d'unité, sans changer de repère "
                         "(pour une pièce qui n'est pas un des cinq corps, par exemple "
                         "une butée)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--simplify", action="store_true",
                   help="décime chaque corps selon TARGET_FACES")
    g.add_argument("--faces", type=int, metavar="N",
                   help="décime chaque pièce à N faces au plus")
    args = ap.parse_args()

    parts = args.parts.split(",") if args.parts else BODIES
    if args.simplify:
        targets = TARGET_FACES
    elif args.faces:
        targets = {name: args.faces for name in parts}
    else:
        targets = None

    sys.exit(main(args.in_dir, args.out_dir, parts, args.input_ext,
                  args.input_units, args.units_only, targets, args.ref_dir))
