######################################
Télécharger les paquets et dépendances
######################################

Dans l'état actuel des choses la méthode à privilégier pour utiliser le présent projet est de cloner le dépôt GitHub et de construire les paquets à partir des sources.

***********************
Télécharger les paquets
***********************

Les paquets sources sont disponibles sur le dépôt GitHub suivant : `pantographe_dessin_robotise <https://github.com/aallonas/pantographe_dessin_robotise>`_.

.. code-block:: bash

   cd ~
   git clone https://github.com/aallonas/pantographe_dessin_robotise.git

***********************
Présentation des paquets
***********************

- ``pantographe_description`` : description URDF/xacro du robot pantographe.
- ``pantographe_hardware`` : interface matérielle ROS 2 pour le pantographe.
- ``pantographe_controller`` : contrôleurs ROS 2 pour le pantographe.
- ``pantographe_bringup`` : fichiers de lancement pour le pantographe.

.. code-block:: bash
   cd ~/pantographe_dessin_robotise/ros2_ws/

***********************
construire les paquets
***********************

.. code-block:: bash

   cd ~/pantographe_dessin_robotise/ros2_ws/
   colcon build --symlink-install
   source ~/pantographe_dessin_robotise/ros2_ws/install/setup.bash 

.. tip::
   Pour éviter de devoir sourcer le workspace à chaque nouvelle session terminal,
   ajoutez la ligne suivante à votre fichier ``~/.bashrc`` : `source ~/pantographe_dessin_robotise/ros2_ws/install/setup.bash `

   .. code-block:: bash

      echo "source ~/pantographe_dessin_robotise/ros2_ws/install/setup.bash" >> ~/.bashrc

Pour plus d'informations sur la construction de paquets ROS 2, consultez la documentation officielle : `ROS 2 Tutorials <https://docs.ros.org/en/jazzy/Tutorials.html>`_.

