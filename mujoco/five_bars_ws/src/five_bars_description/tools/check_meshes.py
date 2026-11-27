#!/usr/bin/env python3
"""Vérifie que les maillages de meshes/ sont utilisables par MuJoCo et par l'URDF.

Quatre contrôles par fichier, puis un essai de chargement du modèle complet :

  1. FORMAT   STL binaire, en-tête cohérente avec la taille du fichier.
  2. FACES    au plus 200 000 faces : au-delà, MuJoCo refuse le fichier
              (« stl_decoder: number of faces should be between 1 and 200000 »).
  3. UNITES   le modèle est en mètres. Une pièce de ce robot fait au plus ~0,4 m ;
              une boîte englobante de plusieurs dizaines d'unités trahit des
              millimètres, et tout sera 1000 fois trop grand.
  4. REPERE   la boîte englobante est comparée à celle attendue pour ce corps
              (repère local du corps, origine sur le pivot proximal ; R0 pour le
              bâti). Un maillage laissé dans le repère de l'assemblage CAO est
              détecté ici.

Usage :
    python3 tools/check_meshes.py                 # vérifie meshes/ et mjcf/five_bars.xml
    python3 tools/check_meshes.py autre/dossier
    python3 tools/check_meshes.py --ref           # réaffiche les boîtes attendues
"""
import glob
import os
import struct
import sys

MAX_FACES = 200_000          # limite du décodeur STL de MuJoCo
MAX_EXTENT_M = 1.0           # aucune pièce du 5 barres ne dépasse 1 m

#: Boîtes englobantes attendues, en mètres, dans le repère du corps.
#: (min_x, min_y, min_z, max_x, max_y, max_z), tolérance de quelques mm.
EXPECTED = {
    "base":  (-0.120, -0.100, -0.011, 0.280, 0.240, 0.121),
    "link1": (-0.011, -0.015,  0.049, 0.095, 0.015, 0.113),
    "link2": (-0.015, -0.015,  0.077, 0.172, 0.032, 0.108),
    "link3": (-0.015, -0.015,  0.057, 0.162, 0.015, 0.113),
    "link4": (-0.011, -0.015,  0.049, 0.094, 0.015, 0.108),
    # Butées, rigidement fixées au bâti : même repère que lui (R0).
    # Fournies à part, référencées ni par le MJCF ni par l'URDF pour l'instant.
    "stopper_01": (0.181, -0.002, 0.048, 0.185, 0.002, 0.083),
    "stopper_02": (0.114,  0.037, 0.048, 0.117, 0.041, 0.083),
}
TOL_M = 0.005                # 5 mm de tolérance sur la boîte englobante


def read_stl(path):
    """Retourne (nombre_de_faces, bounds) pour un STL binaire, sans dépendance."""
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        header = fh.read(84)
        if len(header) < 84:
            raise ValueError("fichier trop court pour un STL binaire")
        if header[:5].lstrip().lower().startswith(b"solid") and 84 + 50 * struct.unpack(
                "<I", header[80:84])[0] != size:
            raise ValueError("STL ASCII (MuJoCo veut du binaire)")
        n = struct.unpack("<I", header[80:84])[0]
        if 84 + 50 * n != size:
            raise ValueError(f"taille incohérente : en-tête annonce {n} faces "
                             f"soit {84 + 50 * n} octets, le fichier en fait {size}")
        lo = [float("inf")] * 3
        hi = [float("-inf")] * 3
        for _ in range(n):
            rec = fh.read(50)
            vals = struct.unpack("<12f", rec[:48])
            for v in range(1, 4):                      # 0 = normale
                for a in range(3):
                    x = vals[3 * v + a]
                    lo[a] = min(lo[a], x)
                    hi[a] = max(hi[a], x)
    return n, (lo, hi)


def check(path):
    name = os.path.splitext(os.path.basename(path))[0]
    problems, notes = [], []
    try:
        n, (lo, hi) = read_stl(path)
    except ValueError as e:
        return [f"FORMAT : {e}"], []

    notes.append(f"{n} faces, {os.path.getsize(path) / 1e6:.2f} Mo")
    if n > MAX_FACES:
        problems.append(f"FACES : {n} > {MAX_FACES}, MuJoCo refusera ce fichier")

    ext = [hi[a] - lo[a] for a in range(3)]
    notes.append("boîte (m) min=[" + ", ".join(f"{v:.4f}" for v in lo)
                 + "] max=[" + ", ".join(f"{v:.4f}" for v in hi) + "]")
    if max(ext) > MAX_EXTENT_M:
        problems.append(f"UNITES : la pièce mesure {max(ext):.1f} unités de long. "
                        f"C'est sans doute des millimètres ; divisez par 1000.")

    exp = EXPECTED.get(name)
    if exp is None:
        notes.append("REPERE : pas de référence pour ce nom, contrôle ignoré")
    else:
        got = tuple(lo) + tuple(hi)
        off = max(abs(g - e) for g, e in zip(got, exp))
        if off > TOL_M:
            problems.append(
                f"REPERE : boîte décalée de {off * 1000:.0f} mm par rapport à "
                f"l'attendu. Le maillage est probablement resté dans le repère de "
                f"l'assemblage CAO : passez-le par tools/convert_cad.py.")
        else:
            notes.append(f"REPERE : conforme (écart max {off * 1000:.1f} mm)")
    return problems, notes


def main(mesh_dir):
    files = sorted(glob.glob(os.path.join(mesh_dir, "*.stl")))
    if not files:
        print(f"aucun .stl dans {mesh_dir}", file=sys.stderr)
        return 1
    bad = 0
    for f in files:
        problems, notes = check(f)
        mark = "FAIL" if problems else " ok "
        print(f"[{mark}] {os.path.basename(f)}")
        for n in notes:
            print(f"        {n}")
        for p in problems:
            print(f"        !! {p}")
        bad += bool(problems)

    mjcf = os.path.join(os.path.dirname(os.path.abspath(mesh_dir)), "mjcf", "five_bars.xml")
    if os.path.exists(mjcf):
        print()
        try:
            import mujoco
            m = mujoco.MjModel.from_xml_path(mjcf)
            print(f"[ ok ] {mjcf} se charge : {m.nmesh} meshes, {m.nmeshface} faces")
        except ImportError:
            print("[ -- ] mujoco non installé ici, chargement du modèle non testé")
        except Exception as e:
            bad += 1
            print(f"[FAIL] {mjcf} ne se charge pas :\n        {e}")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--ref" in sys.argv:
        print("Boîtes englobantes attendues (mètres, repère du corps) :")
        for k, v in EXPECTED.items():
            print(f"  {k:6s} min=({v[0]:+.3f}, {v[1]:+.3f}, {v[2]:+.3f})  "
                  f"max=({v[3]:+.3f}, {v[4]:+.3f}, {v[5]:+.3f})")
        sys.exit(0)
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "meshes")))
