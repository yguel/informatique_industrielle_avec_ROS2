#################################
Création du fichier URDF du robot
#################################

.. warning::
   **Fichier URDF non finalisé**
   
   Ce fichier URDF est encore en cours de développement. Il manque actuellement l'intégration des marqueurs **ros2_control** nécessaires pour l'interfaçage avec les contrôleurs matériels. Ces éléments seront ajoutés dans une version ultérieure de la documentation.

Le modèle URDF du robot pantographe est défini à l'aide d'un fichier **xacro** nommé
``pantographe.urdf.xacro``, situé dans le package
``pantographe_description``.

L'utilisation du format **xacro** permet de simplifier et de structurer la description
du robot en introduisant des **macros**, des **variables** et des **paramètres**,
évitant ainsi la redondance inhérente à un fichier XML URDF statique.

La documentation officielle de xacro est disponible à l'adresse suivante :
https://wiki.ros.org/xacro

Principe des fichiers URDF et xacro
===================================

Les fichiers **URDF** et **xacro** permettent de décrire la structure mécanique d'un
robot en définissant :

- des **liens rigides** (*links*),
- des **mobilités** (*joints*) reliant ces liens,
- ainsi que des informations supplémentaires telles que :
  
  - les propriétés **visuelles**,
  - les volumes de **collision**,
  - les paramètres **d'inertie**.

Afin d'améliorer la cohérence du modèle et de faciliter sa compréhension,
les fichiers de géométrie ont été **réexportés** de manière à corriger le placement
des **origines** et l'orientation des **axes** de chaque lien.

Organisation des fichiers xacro
================================

La description du robot est divisée en plusieurs fichiers xacro :

- un fichier principal contenant la structure générale du robot ;
- un ou plusieurs fichiers de **macros xacro** décrivant les composants répétitifs
  (liens, joints, transmissions, etc.).

Exemple de fichier définissant les macros xacro :

.. code-block:: xml

   <?xml version="1.0"?>
   <robot xmlns:xacro="http://ros.org/wiki/xacro" name="pantographe_macros">

     <!--
       Macros for pantographe description
       - link_with_mesh: creates a link with inertial, visual and collision referencing meshes/<name>
       - revolute_joint: creates a revolute joint about Z between parent and child
     -->

     <xacro:macro name="link_with_mesh" params="name mesh mass ixx iyy izz">
       <link name="${name}">
         <inertial>
           <origin xyz="0 0 0" rpy="0 0 0"/>
           <mass value="${mass}"/>
           <inertia ixx="${ixx}" ixy="0.0" ixz="0.0" iyy="${iyy}" iyz="0.0" izz="${izz}"/>
         </inertial>

         <visual>
           <origin xyz="0 0 0" rpy="0 0 0"/>
           <geometry>
             <mesh filename="package://pantographe_description/meshes/${mesh}"/>
           </geometry>
         </visual>

         <collision>
           <origin xyz="0 0 0" rpy="0 0 0"/>
           <geometry>
             <mesh filename="package://pantographe_description/meshes/${mesh}"/>
           </geometry>
         </collision>
       </link>
     </xacro:macro>

     <xacro:macro name="revolute_joint" params="name parent child xyz rpy axis lower upper effort velocity">
       <joint name="${name}" type="revolute">
         <parent link="${parent}"/>
         <child  link="${child}"/>
         <origin xyz="${xyz}" rpy="${rpy}"/>
         <axis xyz="${axis}"/>
         <limit lower="${lower}" upper="${upper}" effort="${effort}" velocity="${velocity}"/>
       </joint>
     </xacro:macro>

   </robot>

Exemple de fichier URDF principal utilisant les macros :

.. code-block:: xml
   
      <?xml version="1.0"?>
   <robot name="pantographe" xmlns:xacro="http://ros.org/wiki/xacro">
   
     <!--
       Xacro file for the pantographe model.
       Links: base, link1, link2, link3, link4
       Meshes expected at: package://pantographe_description/meshes/base.dae and link1.dae..link4.dae
   
       Notes:
       - There are 5 joints forming a closed chain.
       - Since URDF does not natively support closed kinematic loops, this file will ommit closing the 
         chain by ignoring joint3 between link2 and link3.
       - Joint 1 and 5 are the only driven joints. 
       -->
   
     <xacro:include filename="$(find pantographe_description)/urdf/pantographe_macros.urdf.xacro"/>
   
     <!-- links:  -->
     <xacro:link_with_mesh name="base"  mesh="base.dae"  mass="2.0"  ixx="0.02" iyy="0.02" izz="0.02"/>
     <xacro:link_with_mesh name="link1" mesh="link1.dae" mass="0.5"  ixx="0.005" iyy="0.005" izz="0.005"/>
     <xacro:link_with_mesh name="link2" mesh="link2.dae" mass="0.5"  ixx="0.005" iyy="0.005" izz="0.005"/>
     <xacro:link_with_mesh name="link3" mesh="link3.dae" mass="0.5"  ixx="0.005" iyy="0.005" izz="0.005"/>
     <xacro:link_with_mesh name="link4" mesh="link4.dae" mass="0.5"  ixx="0.005" iyy="0.005" izz="0.005"/>
   
     <!-- joints: revolute about y. origins mesured in cad -->
     <xacro:revolute_joint name="joint1" parent="base"  child="link1" xyz="-0.0800 0.0320 0.0700" rpy="-1.57079 1.57079 0" axis="0 0 1" lower="-3.1416" upper="3.1416" effort="10" velocity="5"/>
     <xacro:revolute_joint name="joint5" parent="base" child="link4" xyz="0.0580 0.0320 0.0700" rpy="-1.57079 1.57079 0" axis="0 0 1" lower="-3.1416" upper="3.1416" effort="10" velocity="5"/>
     <xacro:revolute_joint name="joint2" parent="link1" child="link2" xyz="0.0800 0.0000 0.0540" rpy="1.57079632679 0 3.14159" axis="0 1 0" lower="-3.1416" upper="3.1416" effort="10" velocity="5"/>
     <xacro:revolute_joint name="joint4" parent="link4" child="link3" xyz="0.0790 0.0000 0.0530" rpy="-1.57079 0 $(radians(180))" axis="0 1 0" lower="-3.1416" upper="3.1416" effort="10" velocity="5"/>
   
   </robot>

Génération du fichier URDF
==========================

Le fichier URDF final est généré à partir du fichier xacro à l'aide de la commande
suivante, exécutée dans un terminal situé à la racine de l'espace de travail ROS 2 :

.. code-block:: bash

   ros2 run xacro xacro \
     pantographe_description/urdf/pantographe.urdf.xacro \
     > pantographe.urdf

Cette commande produit un fichier ``pantographe.urdf`` entièrement résolu,
qui peut ensuite être utilisé par les outils ROS 2 tels que **RViz**,
**robot_state_publisher** ou les simulateurs.

