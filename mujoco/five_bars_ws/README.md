# Système 5 barres (pantographe porte-stylo) — MuJoCo + ROS 2 Jazzy + ros2_control

Simulation MuJoCo du système 5 barres du cours
[Informatique industrielle avec ROS 2](https://yguel.github.io/informatique_industrielle_avec_ROS2/p00_5_bars_system_pencil_holder_with_rpi_and_dynamixel/p50s02_mechanical_description.html),
construite à partir des modèles STEP/COLLADA du cours (`maquette-5-barres_asm.stp`, `base`, `link1..4`).

| Demande | Où |
|---|---|
| 1. GUI Python + MuJoCo pour régler `q1`, `q4` | `src/five_bars_mujoco/five_bars_mujoco/direct_gui.py` |
| 2. Hardware interface ros2_control vers MuJoCo | `src/five_bars_hardware/` (plugin `five_bars_hardware/MujocoTopicSystem`) |
| 3. Simulateur et GUI reliés par topic (le même que ros2_control) | `sim_node.py`, `slider_gui_node.py`, topic `/five_bars/joint_commands` |
| 4. Mise à jour de l'état complet (chaîne fermée) avec MuJoCo | `state_updater_node.py` → `/joint_states` |
| 5. Docker MuJoCo + 5 barres + Google Test | `docker/` (`Dockerfile`, `docker-compose.yml`, `start.sh`) |
| 6. Tests (qui échouent) des modèles direct/inverse, vérifiés par MuJoCo headless | `src/five_bars_kinematics/test/` + `.github/workflows/ci.yml` |

## Modèle et conventions

![schéma](https://yguel.github.io/informatique_industrielle_avec_ROS2/_images/schema_cinematique.svg)

* Repère **R0** du schéma : origine **A1** (moteur gauche), `x0` vers **A5** (moteur droit), `z0` vers le haut.
* **`q1`** = angle **absolu** du bras gauche A1A2 / `x0` ; **`q4`** = angle **absolu** du bras droit A5A4 / `x0`.
  Dans le MJCF comme dans l'URDF, la valeur des liaisons `joint_q1` / `joint_q4` **est** `q1` / `q4`.
* Pivots passifs `joint_A2` (link1→link2) et `joint_A4` (link4→link3) : angles **relatifs**.
* La boucle est fermée en **A3** par une contrainte MuJoCo `<connect site1="A3_link2" site2="A3_link3"/>`.
* Le stylo (site `pen_tip`) est fixé sur l'avant-bras gauche `link2`, **décalé** de A3 :
  `P = A3 + pen_dx·u2 + pen_dy·v2` (u2 le long de A2→A3, v2 à sa gauche).

### Géométrie : schéma vs CAO — ⚠️ à lire

Toutes les cotes sont dans **`src/five_bars_description/config/geometry.yaml`** (source unique : le MJCF
est généré à partir de ce fichier, l'URDF le lit via xacro, les tests relisent la géométrie dans le MJCF).

Les cotes ont été **mesurées sur la CAO** (`tools/measure_cad.py`, ajustement de cercles sur les alésages) :

| | schéma du cours | CAO (utilisé) |
|---|---|---|
| l0 = A1A5 | 137,98 mm | 137,99 mm |
| l1 = A1A2 | 80 mm | 80,0 mm |
| l2 = A2A3 | 146,3 mm | **157,0 mm** |
| l3 = A3A4 | 146,3 mm | **147,0 mm** |
| l4 = A4A5 | 80 mm | **79,0 mm** |
| stylo / A3 (repère link2) | « à mesurer » | **-16,0 mm** le long de A2A3, **+21,0 mm** à gauche |

Les maillages ne se referment que sur les cotes CAO, d'où ce choix. Pour utiliser les cotes du schéma
(ou celles mesurées sur votre robot) : éditez `geometry.yaml`, puis
`python3 src/five_bars_description/tools/generate_models.py`.

### Outils CAO (`src/five_bars_description/tools/`)

* `measure_cad.py <dossier_dae>` : mesure A1…A5, longueurs et décalage du stylo sur les `.dae` du cours.
* `convert_cad.py <dossier_dae> meshes/` : `.dae` (repère assemblage) → `.stl` allégés dans le repère de chaque corps.
* `generate_models.py` : `geometry.yaml` → `mjcf/five_bars.xml`.

Les `.dae`/`.stp` sont dans le dépôt du cours : `cad/pentograph/`.

## Architecture ROS 2

```
 slider_gui ─────────┐                       (std_msgs/Float64MultiArray, data=[q1, q4] rad)
                     ├──► /five_bars/joint_commands ──► sim_node (MuJoCo, viewer optionnel)
 ros2_control        │                                       │
  forward_position_controller ─► MujocoTopicSystem.write() ──┘
                                 MujocoTopicSystem.read() ◄── /five_bars/sim/actuated_joint_states
  joint_state_broadcaster ─► /joint_state_broadcaster/joint_states (q1, q4)
                                       │
                         state_updater (MuJoCo : fermeture de chaîne)
                                       └─► /joint_states (q1, A2, q4, A4) ─► robot_state_publisher ─► TF ─► RViz
```

* **Hardware interface** (`MujocoTopicSystem`) : 2 joints `joint_q1`, `joint_q4` ; commande `position`,
  états `position/velocity/effort`. `write()` publie sur le **même topic** que l'IHM, uniquement quand la
  consigne change (`publish_only_on_change`) : IHM et ros2_control cohabitent. Le nœud ROS du composant
  est celui fourni par le framework (`get_node()`), animé par le controller_manager (API ros2_control ≥ 4.3x de Jazzy).
  Pour passer au vrai robot, il suffit de remplacer la balise `<hardware>` de l'URDF par un driver Dynamixel.
* **state_updater** : seuls `q1`, `q4` sont mesurés ; il impose ces angles dans sa propre instance du
  modèle MuJoCo et résout la fermeture en A3 (Newton sur `joint_A2`, `joint_A4` avec les jacobiennes
  `mj_jacSite`), en partant de la solution précédente (on reste sur la même branche d'assemblage), puis
  calcule les vitesses passives (`dq_p = -J_p⁺ J_a dq_a`). Il marche aussi avec le robot réel.
* `sim_node` publie aussi la vérité terrain `/five_bars/sim/joint_states` (toutes les liaisons) et
  `/five_bars/sim/pen_position`, et offre le service `~/reset`.

## Quick start (`docker/start.sh`)

Tout ce qui concerne Docker est dans `docker/` ; les sources (`src/`) sont montées depuis `../src`.
Le script peut être lancé depuis n'importe quel dossier :

```bash
docker/start.sh              # build the image the first time (~10 min), then open a shell in the container
docker/start.sh --rebuild    # force a rebuild of the image
docker/start.sh test         # run all tests headless (same as the CI)
docker/start.sh ros2 run five_bars_mujoco direct_gui   # run a single command
```

Inside the container, the MuJoCo standalone example (no ROS nodes involved):

```bash
ros2 run five_bars_mujoco direct_gui                 # sliders q1 / q4 + MuJoCo 3D viewer
ros2 run five_bars_mujoco direct_gui --no-viewer     # sliders only (no OpenGL needed)
python3 -m mujoco.viewer --mjcf=/ws/install/five_bars_description/share/five_bars_description/mjcf/five_bars.xml
                                                     # raw MuJoCo viewer (Control panel > act_q1 / act_q4)
```

## Utilisation avec Docker

```bash
xhost +local:docker                                        # affichage X11 depuis le conteneur (Linux)
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run --rm dev   # shell ; ../src est monté dans /ws/src
# dans le conteneur, après modification des sources :
colcon build && source install/setup.bash
```

1. **GUI directe** (sans ROS) : `ros2 run five_bars_mujoco direct_gui`
2. **Simulateur + IHM par topic** : `ros2 launch five_bars_bringup sim_gui.launch.py rviz:=true`
3. **ros2_control + simulateur** :
   ```bash
   ros2 launch five_bars_bringup ros2_control_sim.launch.py gui:=true rviz:=true
   ros2 topic pub --once /forward_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [2.2, 1.0]}"
   ```
   Option `use_viewer:=false` pour une simulation headless.

## Tests unitaires (TDD) : modèles géométriques direct et inverse

À implémenter :

* C++ : `src/five_bars_kinematics/src/kinematics.cpp` (`forwardKinematics`, `inverseKinematics`, voir le `.hpp`) ;
* Python : `src/five_bars_kinematics/five_bars_kinematics/kinematics.py` (`forward_kinematics`, `inverse_kinematics`).

Les tests (`test_kinematics.cpp` en **gtest**, `test_kinematics.py` en **unittest**) prennent la **simulation MuJoCo
headless** comme vérité terrain : consignes envoyées aux servos simulés, attente de l'équilibre, lecture du site
`pen_tip`. Ils vérifient : position du stylo (0,1 mm), décalage du stylo, angles retrouvés par l'IK (1e-3 rad),
atteinte de cibles d'une zone de dessin après asservissement simulé (0,5 mm), `IK∘FK = id`, cas non assemblables / inatteignables.

```bash
docker/start.sh test                                     # même chose que la CI
docker compose -f docker/docker-compose.yml run --rm test  # idem via compose (rapports JUnit dans test_results/)
# ou dans le conteneur :
colcon test --packages-select five_bars_kinematics --event-handlers console_direct+ && colcon test-result --verbose
python3 -m unittest discover -s src/five_bars_kinematics/test -p "test_*.py" -v
./build/five_bars_kinematics/test_kinematics_cpp
```

État initial attendu : **les tests de cinématique échouent** ; seuls les tests `SimulationHarness` /
`TestSimulationHarness` (qui valident le banc de test) et ceux de `five_bars_mujoco` passent.
La CI GitHub (`.github/workflows/ci.yml`) construit l'image, lance tous les tests et publie le rapport JUnit :
elle sera rouge tant que la cinématique n'est pas implémentée.

La bibliothèque C de MuJoCo utilisée par gtest est celle de la roue pip `mujoco` (`cmake/FindMuJoCo.cmake`) :
Python et C++ utilisent la même version. Pour une archive officielle, définir `MUJOCO_DIR`.

## Notes

* macOS : le viewer passif MuJoCo nécessite `mjpython` à la place de `python3`.
* Les débattements des servos (`limits` dans `geometry.yaml`) : q1 ∈ [30°, 170°], q4 ∈ [10°, 150°].
* Servos simulés : actionneurs de position (kp = 8 N·m/rad, couple max 1,5 N·m comme l'AX-12A),
  consigne limitée à 6 rad/s.
