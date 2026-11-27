*************************************
Rappels : setup ROS2
*************************************

.. note::

   Ce chapitre, et les suivants, s'appuient sur **Docker**. Si vous ne l'avez pas encore
   sur votre machine, installez-le en suivant :doc:`p02s00_install_docker`.

   **Si Docker est déjà installé, ne le réinstallez pas.** Une commande suffit à le
   vérifier :

   .. code-block:: bash

      docker run --rm hello-world

   Si vous voyez ``Hello from Docker!``, tout est en place et vous pouvez continuer.
   Sinon, la page :ref:`install_docker` explique quoi faire selon le message obtenu.

Un projet ROS2 se compile et s'exécute dans ce que l'on appelle un ``workspace`` souvent abrévié en ``ws`` dans lequel se trouve un répertoire ``src`` qui contient les packages ROS2 que vous allez créer ou que vous allez utiliser.

.. code-block:: bash

   cd ~/info_indus/
   mkdir -p ros2_ws/src

Nous allons maintenant utiliser un package ROS2 que nous allons installer dans le répertoire ``src`` de votre workspace ROS2.

Il s'agit du **tutoriel SCARA**, dans sa version ``ecat_ros2_workshop`` :

.. code-block:: bash

   cd ~/info_indus/ros2_ws/src
   git clone https://github.com/ICube-Robotics/ecat_ros2_workshop

.. note::

   Tout le cours utilise **ROS 2 Jazzy**. Pour vérifier la distribution installée sur
   votre machine :

   .. code-block:: bash

      printenv ROS_DISTRO      # si l'environnement ROS 2 est déjà chargé
      ls /opt/ros              # sinon : la liste des distributions installées

Afin d'accélerer les processus de compilation et d'exécution, nous allons utiliser des macros bash qui facilitent la tâche quand on utilise la suite d'outils ROS2 centrée sur ``colcon``.

Ouvrez votre fichier ``~/.bashrc`` avec vscode:

.. code-block:: bash

   code ~/.bashrc

Ajoutez à la fin du fichier les lignes suivantes:

.. literalinclude:: resources/code/_.bashrc
   :language: bash
   :caption: Addons au fichier .bashrc
   :linenos:

Enregistrez le fichier et fermez vscode.

Rechargez votre fichier ``~/.bashrc`` pour prendre en compte les modifications:

.. code-block:: bash

   source ~/.bashrc

Vous pouvez maintenant utiliser les macros bash que vous venez de définir.

*************************************************
Premiers pas avec le tutoriel SCARA
*************************************************

Nous allons maintenant compiler le tutoriel SCARA que nous venons de cloner, à l'aide des macros bash que nous venons de définir.

.. code-block:: bash

   cd ~/info_indus/ros2_ws
   sudo apt-get update
   ros2_jazzy
   ros2_build

.. warning::

   Vérifiez au passage la **branche** du dépôt cloné : un projet ROS 2 a souvent une
   branche par distribution. ``git branch -a`` les liste, ``git switch <branche>`` bascule.

Si tout s'est bien passé, vous devriez voir un message de succès à la fin de la compilation.

.. code-block:: bash

   #All required rosdeps installed successfully
   Starting >>> scara_description
   Starting >>> scara_bringup
   Starting >>> scara_joint_velocity_controller
   Starting >>> scara_nodes
   Finished <<< scara_description [0.88s]                                                               
   Starting >>> scara_hardware
   Finished <<< scara_nodes [0.90s]                                  
   Finished <<< scara_bringup [1.14s]                                  
   Finished <<< scara_hardware [4.50s]                                                     
   Finished <<< scara_joint_velocity_controller [8.28s]                     

   Summary: 5 packages finished [8.52s]


.. note::

   ``ros2_jazzy`` est un alias qui charge l'environnement ROS2 de la distribution jazzy.
   ``ros2_build`` est un alias qui installe les dépendences et compile tout le workspace ROS2 courant.

===========================
Extension vscode pour ROS2
===========================

Pour faciliter la rédaction de code ROS2, il est très utile d'installer les extensions suivantes:

#. ``ROS2`` de nonanonno (nonanonno.vscode-ros2)
#. ``RO2`` de JaehyunShim (jaehyunshim.vscode-ros2)
#. ``ROS 2 Ament Task Provider`` de Allison Thackston (althack.ament-task-provider)


===============================================
Créer la description URDF physique d'un robot 
===============================================

Pour créer la description URDF physique d'un robot, suivez dans l'ordre :

#. `tutoriel URDF <https://icube-robotics.github.io/ecat_ros2_workshop/tutorials/urdf_tutorial/>`_
#. `Comment lancer et intéragir avec le système courant <https://icube-robotics.github.io/ecat_ros2_workshop/>`_

===============================================
Créer un projet ROS2 c++ publisher-subscriber
===============================================

Nous allons maintenant créer un nœud ROS2 c++ qui va souscrire au topic ``/joint_states`` et publier sur un topic ``/velocity_supervision`` lorsque la vitesse d'un point physique du robot dépasse un certain seuil.

Pour cela il va falloir créer 2 packages ROS2:

.. code-block:: bash

   cd ~/info_indus/ros2_ws/src
   ros2 pkg create --build-type ament_cmake --license Apache-2.0 scara_velocity_supervision

``ros2 pkg create`` est une commande qui crée un package ROS2 avec le nom donné en argument.
L'option ``--build-type ament_cmake`` indique que le package sera en c++.

Il faudra créer un package dédié au message qui sera transmis sur le topic ``/velocity_supervision``.

.. code-block:: bash

   cd ~/info_indus/ros2_ws/src
   ros2 pkg create --build-type ament_cmake --license Apache-2.0 scara_velocity_supervision_msgs

Étapes:

#. Créez des projets git et enregistrez vos packages sur github.
#. Quelles dépendances ajouter à ces packages?
#. Comment créer un nœud ROS2 c++ qui souscrit à un topic et publie sur un autre topic?
#. Ajoutez les fichiers du projet à votre git et publiez les sur github.
#. Créez une documentation pour chacun de ces 2 packages.
#. Créez le code c++ en utilisant les transformations qui vient vérifier les vitesses de n'importe quel point physique du robot.
#. Documentez votre code.

Une fois ces tâches accomplies nous allons regarder:

#. Comment rendre votre nœud ROS2 paramétrable.
#. Comment tester de manière automatique votre code.