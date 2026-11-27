# `meshes/` — maillages du modèle

Ces cinq fichiers sont les maillages **utilisés tels quels** par le MJCF et par l'URDF :

| Fichier | Lu par | Référence |
|---|---|---|
| `base.stl`, `link1.stl` … `link4.stl` | MuJoCo | `mjcf/five_bars.xml`, `<compiler meshdir="../meshes">` puis `<mesh file="base.stl"/>` |
| les mêmes | ROS 2 / RViz | `urdf/five_bars.urdf.xacro`, `package://five_bars_description/meshes/<nom>.stl` |

Les noms sont donc figés : **pour remplacer un maillage, écrasez le fichier du même nom.**
Rien d'autre n'est à modifier, ni dans le MJCF, ni dans l'URDF, ni dans les tests.

## Les trois contraintes à respecter

1. **Le repère.** Chaque STL est exprimé dans le **repère local de son corps**, pas dans
   le repère de l'assemblage CAO : origine sur le pivot proximal, `x` le long du bras vers
   le pivot distal, `z` vers le haut. Le bâti, lui, est dans `R0` (origine `A1`).
   Un maillage réduit à partir des `.dae` de `cad/pentograph/` est dans le repère CAO et
   sera **mal placé** : voir « D'où viennent ces fichiers » plus bas.
2. **La limite de MuJoCo : 200 000 faces par STL.** Au-delà, le modèle ne se charge pas du
   tout (`stl_decoder: number of faces should be between 1 and 200000`).
3. **L'unité : le mètre**, et le format **STL binaire** (c'est ce qu'exporte `trimesh`).

## Vérifier un maillage de remplacement

```bash
# repère et nombre de faces
python3 -c "import trimesh,sys; m=trimesh.load(sys.argv[1]); \
  print(len(m.faces),'faces, bbox mm', (m.bounds*1000).round(2))" meshes/link1.stl

# le modèle complet se charge-t-il encore ?
python3 -c "import mujoco; m=mujoco.MjModel.from_xml_path('mjcf/five_bars.xml'); \
  print('ok,', m.nmeshface, 'faces au total')"
```

Le `bbox` d'un maillage réduit doit rester celui du maillage remplacé, à la tolérance de
décimation près (quelques dixièmes de mm).

## D'où viennent ces fichiers

Ils sont **générés** à partir des COLLADA du cours, `cad/pentograph/*.dae`, qui sont la
source de vérité. Depuis la racine du dépôt :

```bash
# pleine résolution (défaut) — convient aux quatre bras
python3 src/five_bars_description/tools/convert_cad.py \
        ../../cad/pentograph src/five_bars_description/meshes

# le bâti doit être décimé : 431 266 faces > 200 000
python3 src/five_bars_description/tools/convert_cad.py \
        ../../cad/pentograph /tmp/meshes_base --faces 195000   # puis copier base.stl
```

C'est `convert_cad.py` qui applique le changement de repère (CAO → corps). **Si vous
réduisez un maillage, réduisez le `.stl` de ce dossier** (déjà dans le bon repère), et non
le `.dae` ; si vous partez du `.dae`, repassez par `convert_cad.py` pour replacer le corps.

## État actuel

| Corps | Faces | Taille | Origine |
|---|---:|---:|---|
| `base.stl`   | 105 220 | 5,3 Mo | décimé (la CAO en compte 431 266, au-dessus de la limite MuJoCo) |
| `link1.stl`  | 104 748 | 5,2 Mo | **pleine résolution CAO** |
| `link2.stl`  | 108 136 | 5,4 Mo | **pleine résolution CAO** |
| `link3.stl`  | 164 782 | 8,2 Mo | **pleine résolution CAO** |
| `link4.stl`  |  79 750 | 4,0 Mo | **pleine résolution CAO** |

Total 27 Mo. Le modèle se compile en 0,25 s et les maillages sont purement visuels
(`class="visual"`, `contype="0" conaffinity="0"`) : ils ne coûtent rien à la simulation,
seulement de la mémoire et de la place dans le dépôt.
