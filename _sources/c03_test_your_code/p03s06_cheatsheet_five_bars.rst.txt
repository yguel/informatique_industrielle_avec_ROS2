.. _cheatsheet_five_bars:

##############################################
Aide-mémoire : les commandes du 5 barres
##############################################

.. index::
   5 barres; aide-mémoire
   5 barres; commandes

Toutes les commandes de ce chapitre, rassemblées. Elles sont données **en clair**,
sans raccourci : ce sont celles que vous taperez sur n'importe quelle machine, dans
le conteneur comme en installation native.

Deux conventions pour lire ce qui suit :

* les commandes s'exécutent **depuis la racine de l'espace de travail**,
  ``mujoco/five_bars_ws`` ;
* dans le conteneur, elles se tapent telles quelles. Depuis l'extérieur, préfixez-les
  par ``docker/start.sh`` — par exemple
  ``docker/start.sh ros2 run five_bars_mujoco direct_gui``.

Voir et piloter le robot
========================

.. list-table::
   :header-rows: 1
   :widths: 58 42

   * - Commande
     - Ce que vous obtenez
   * - ``ros2 run five_bars_mujoco direct_gui``
     - les deux curseurs ``q1`` / ``q4`` **et** la fenêtre 3D MuJoCo. C'est le point
       de départ : pas de nœud ROS 2 intermédiaire, la simulation est dans le même
       processus que l'IHM.
   * - ``ros2 run five_bars_mujoco direct_gui --no-viewer``
     - les mêmes curseurs, **sans fenêtre de rendu**. À utiliser en ``ssh``, sur une
       machine sans OpenGL, ou si l'affichage 3D est trop lent.
   * - ``ros2 launch five_bars_bringup sim_gui.launch.py rviz:=true``
     - le simulateur et l'IHM en **nœuds séparés**, reliés par le topic
       ``/five_bars/joint_commands``, plus RViz qui affiche le robot depuis ``/joint_states``.
   * - ``ros2 launch five_bars_bringup ros2_control_sim.launch.py gui:=true rviz:=true``
     - la chaîne complète avec **ros2_control** : le ``controller_manager``, le
       ``forward_position_controller`` et l'interface matérielle qui parle au
       simulateur. C'est l'architecture du vrai robot, avec MuJoCo à la place des servos.

Une fois ``ros2_control_sim.launch.py`` lancé, on commande les deux moteurs depuis un
autre terminal :

.. code-block:: bash

   ros2 topic pub --once /forward_position_controller/commands \
        std_msgs/msg/Float64MultiArray "{data: [2.2, 1.0]}"

.. note::

   Les deux ``launch`` acceptent ``use_viewer:=false`` (pas de fenêtre MuJoCo) et
   ``rviz:=false``. ``ros2_control_sim.launch.py`` a en plus ``gui:=false``, qui retire
   les curseurs. Sur une machine sans affichage, c'est la combinaison à retenir.

   ``direct_gui`` accepte aussi ``--model chemin/vers/five_bars.xml`` pour charger un
   MJCF autre que celui du paquet.

Compiler et tester
==================

.. code-block:: bash

   ros2_jazzy
   ros2_build_reldebug

Ce sont les raccourcis du cours, définis dans le ``~/.bashrc`` du
:doc:`chapitre 2 <../c02_first_ros2_project_pimped/p02s01_pimped_pubsub>` et déjà chargés
dans le conteneur. Ce qu'ils font :

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Raccourci
     - Commandes équivalentes
   * - ``ros2_jazzy``
     - ``source /opt/ros/jazzy/setup.bash``
   * - ``ros2_dep``
     - ``rosdep install --ignore-src --from-paths . -y -r``
   * - ``ros2_build_reldebug``
     - ``ros2_dep && colcon build --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo
       --symlink-install && source install/setup.bash``
   * - ``ros2_build``
     - la même chose en ``Release``, et ``ros2_build_debug`` en ``Debug``

.. warning::

   ``ros2_build_*`` ajoute ``--symlink-install``, alors que l'espace de travail livré
   dans l'image Docker a été compilé **sans**. Au premier usage du raccourci dans le
   conteneur, si ``colcon`` se plaint de ce changement de mode, repartez d'un espace
   propre — une fois suffit :

   .. code-block:: bash

      rm -rf build install && ros2_build_reldebug

   Bonne nouvelle au passage : avec ``--symlink-install``, un maillage modifié dans
   ``src/`` est vu immédiatement, sans recopie dans ``install/``.

.. list-table::
   :header-rows: 1
   :widths: 58 42

   * - Commande
     - Ce qu'elle fait
   * - ``ros2_test``
     - lance les tests de **tous** les paquets
   * - ``ros2_test_only five_bars_kinematics``
     - seulement les tests de la cinématique, ceux que vous devez faire passer
   * - ``ros2_view_tests``
     - le **verdict** : les échecs et leur détail, à lancer après les tests
   * - ``ros2_view_tests_all``
     - le même verdict, tests réussis compris
   * - ``./build/five_bars_kinematics/test_kinematics_cpp``
     - l'exécutable gtest directement, sans passer par colcon
   * - ``python3 -m unittest discover -s src/five_bars_kinematics/test -p "test_*.py" -v``
     - les tests Python seuls

Ce que ces raccourcis recouvrent :

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Raccourci
     - Commande équivalente
   * - ``ros2_test``
     - ``colcon test --ctest-args tests``
   * - ``ros2_test_only <paquet>``
     - ``colcon test --ctest-args "--debug --verbose tests" --packages-select <paquet>``
   * - ``ros2_view_tests``
     - ``colcon test-result``
   * - ``ros2_view_tests_all``
     - ``colcon test-result --all``

.. warning::

   ``colcon test``, et donc ``ros2_test``, renvoie un code de retour qui ne reflète
   **pas** le verdict des tests. C'est ``ros2_view_tests`` qui vous dit si quelque chose
   a échoué : lancez-le toujours derrière, et ne vous fiez pas au silence de
   ``ros2_test``.

Le conteneur Docker
===================

.. list-table::
   :header-rows: 1
   :widths: 58 42

   * - Commande
     - Ce qu'elle fait
   * - ``docker/start.sh``
     - compile l'espace de travail et ouvre un shell dans le conteneur
   * - ``docker/start.sh test``
     - compile puis lance tous les tests, sans fenêtre — exactement ce que fait
       l'intégration continue
   * - ``docker/start.sh <commande>``
     - exécute une seule commande dans le conteneur, puis rend la main
   * - ``docker/start.sh --rebuild``
     - force la reconstruction de l'**image**. Inutile pour un changement de code ou
       de maillage : ``src/`` est monté depuis votre machine.

.. warning::

   Si un conteneur ``five_bars_dev`` tourne déjà, ``docker/start.sh`` ouvre simplement
   un second shell dedans et **ne recompile pas**. Après avoir modifié un maillage ou
   un fichier de description, relancez ``ros2_build_reldebug`` dans le conteneur, ou sortez-en
   et rappelez ``docker/start.sh``. Sinon vous continuerez à voir l'ancienne version :
   MuJoCo et RViz lisent ``install/``, pas ``src/``.

Les maillages et la géométrie
=============================

.. list-table::
   :header-rows: 1
   :widths: 58 42

   * - Commande
     - Ce qu'elle fait
   * - ``python3 src/five_bars_description/tools/check_meshes.py``
     - vérifie les maillages : format, nombre de faces, unités, repère, puis charge
       le modèle complet
   * - ``python3 src/five_bars_description/tools/measure_cad.py ../../cad/pentograph``
     - remesure A1…A5, les longueurs et le décalage du stylo sur la CAO
   * - ``python3 src/five_bars_description/tools/generate_models.py``
     - régénère le MJCF à partir de ``config/geometry.yaml``
   * - ``python3 -m mujoco.viewer --mjcf=install/five_bars_description/share/five_bars_description/mjcf/five_bars.xml``
     - ouvre le modèle seul, sans ROS 2. Le panneau ``Control`` donne ``act_q1`` et
       ``act_q4``. Sur macOS, ``mjpython`` remplace ``python3``.

.. tip::

   Toute la géométrie vient d'un seul fichier, ``src/five_bars_description/config/geometry.yaml``.
   Pour changer une cote — longueur d'un bras, débattement d'un moteur, position du
   stylo — éditez-le puis relancez ``generate_models.py`` : le MJCF et l'URDF suivent.
