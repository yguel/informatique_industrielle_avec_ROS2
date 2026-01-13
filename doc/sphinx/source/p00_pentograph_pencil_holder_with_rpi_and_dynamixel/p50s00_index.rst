#########################################################
Pantographe de dessin robotisé avec Raspberry Pi et ROS2
#########################################################



.. figure:: resources/img/real_system_photo.png
   :align: center

=====================
Description du projet
=====================

.. Pour ce travail pratique, vous allez installer une plateforme robotique ROS2 sur un Raspberry Pi (Pi5) et documenter le projet.

L'objectif de ces travaux pratiques et de faire fonctionner la plateforme robotique, pentographe avec ROS2 sur un Raspberry Pi (Pi5) et documenter le projet.
Le projet consiste donc à:

.. #. installer Ubuntu sur le Raspberry Pi, 
.. #. installer ROS2,
.. #. Tester et documenter les tests de l'installation système 

#. Décrire la plateforme mécanique
#. Décrire le matériel électronique, carte dynamixel avec les liens sur les documentations techniques (datasheets)
#. Créer la rerprésentation mécanique du pantographe dans un fichier URDF
#. Visualiser le résultat avec RVIZ
#. Décrire la dynamique et donner les équations pour piloter la position de l'organe terminal du pentographe: comment 
#. Créer un package ROS2 pour contrôler le pantographe
#. Créer des tests et documenter les tests
#. Créer un code pour dessiner avec le pentographe
#. Tester en réel avec le pantographe
#. Créer un code de simulation pour le pentographe
#. Tester en simulation avec Gazebo et RViz

La documentation correspondra à un fork de ce projet et sera publiée sur votre github.
Dans ce projet un canevas de documentation est fourni. Vous devrez le compléter et le publier.
Vous soumettrez votre travail sous forme de push request à ce projet.

Vous serez évalué sur la qualité de la documentation de votre projet et le pilotage du pentographe réel.

.. toctree::
   :maxdepth: 2

   p50s01_material_description
   p50s02_mechanical_description
   p50s05_ubuntu
   p50s04_ROS2
   p50s03_urdf
   p50s06_dynamixel
   p50s07_rviz
