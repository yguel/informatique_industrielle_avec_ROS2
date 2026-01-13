###################################################
 Génération de la description URDF du pantographe
###################################################

Nous allons utiliser le modèle 3D au format step conçu et réalisé par M. Olivier PICCIN pour générer la description URDF du pantographe.

.. figure:: resources/img/pantograph_step_model.png
   :align: center

Il s'agit d'un assemblage comportant 5 pièces principales :

  #. BATI_ASM: le bâti de la strucuture du pantographe avec les 2 moteurs pas à pas. Dans l'URDF nous allons le nommer ``base``.
  #. LINK1_ASM: le bras gauche du pantographe. Dans l'URDF nous allons le nommer ``link1``.
  #. LINK2_ASM: l'avant bras gauche du pantographe. Dans l'URDF nous allons le nommer ``link2``.
  #. LINK3_ASM: l'avant bras droit du pantographe. Dans l'URDF nous allons le nommer ``link3``.
  #. LINK4_ASM: le bras droit du pantographe. Dans l'URDF nous allons le nommer ``link4``.

:download:`maquette-5-barres_asm.stp <resources/cad/maquette-5-barres_asm.stp>`

Du point de vue URDF, nous aurons aussi besoin de définir l'outil de travail: le crayon et donc de le référencer par rapport à son support qui se trouve être sur l'avant bras gauche du pentographe (``link2``).

Dans un fichier URDF, les modèles 3D sont utilisés à partir de fichiers collada (extension .dae).
Il va donc falloir convertir notre modèle 3D au format step en un ensemble de 5 modèles 3D au format collada.

==================================
Extraction des modèles 3D en step
==================================

Pour extraire les modèles 3D au format step, vous pouvez utiliser le logiciel freecad.
   
   #. :download:`base.stp <resources/cad/base.stp>`
   #. :download:`link1.stp <resources/cad/link1.stp>`
   #. :download:`link2.stp <resources/cad/link2.stp>`
   #. :download:`link3.stp <resources/cad/link3.stp>`
   #. :download:`link4.stp <resources/cad/link4.stp>`

=====================================
Conversion des modèles 3D en collada
=====================================

Pour convertir les modèles 3D en collada (dae), vous pouvez utiliser le logiciel freecad.
   
   #. :download:`base.dae <resources/cad/base.dae>`
   #. :download:`link1.dae <resources/cad/link1.dae>`
   #. :download:`link2.dae <resources/cad/link2.dae>`
   #. :download:`link3.dae <resources/cad/link3.dae>`
   #. :download:`link4.dae <resources/cad/link4.dae>`

=========================
Création du fichier URDF
=========================

Le fichier URDF du pantographe est disponible en ressource :

**ERREUR : Placement des repères au sein des fichiers**

Les fichiers URDF référencent les maillages 3D par rapport au repère local de chaque lien. Pour garantir la validité de la simulation, il est impératif de vérifier la position des repères (frames) des fichiers 3D.

Une erreur de référencement provoque des décalages visuels ce qui donne des repères compliqué à utilisé car il ne sont pas centré sur une des deux liaisons.

**Action corrective requise :**
* **Réexporter les fichiers 3D individuellement.**
* **Référencement local :** Chaque pièce doit être exportée par rapport à son propre repère d'origine placé sur une de ses liaisons.

Pour définir le fichier URDF, nous avons repris la structure du fichier URDF du SCARA disponible dans le dépôt github. Ensuite, il faut changer les parties correspondantes aux liens et aux joints.

Voici un extrait du fichier URDF du pantographe avec les détails du Link 1 et Joint 1
-------------------------------------------------------------------------------------

Voici l'extrait du fichier URDF correspondant à l'articulation principale :

.. code-block:: xml

   <link name="link1">
     <visual>
       <geometry>
         <mesh filename="file:///home/ada/ws1612/src/ecat_ros2_workshop/scara_description/urdf/meshes/link1.dae"/>
       </geometry>      
       <origin xyz="0 0 0" rpy="0 0 0"/>
     </visual>
   </link>

   <joint name="joint1" type="revolute">
      <parent link="base_link"/>
      <child link="link1"/>
      <origin xyz="-0.08 -0.07 0.035" rpy="0 0 0"/>
      <axis xyz="0 0 1"/>
      <limit lower="-3.14" upper="3.14" effort="10" velocity="1.0"/>
   </joint>

Explication technique
---------------------

* **Origin du Joint** : Définit la position du repère de l'enfant (`link1`) par rapport au parent (`base_link`). Il faut donc récupérer les coordonnées exactes de l'axe de rotation du joint dans l'assemblage global. Cela peut être fait en utilisant un logiciel de CAO pour mesurer la position de l'axe de rotation par rapport au repère global de l'assemblage.
* **Origin du Visual** : Comme elle est à ``0 0 0``, le centre du fichier ``link1.dae`` doit correspondre exactement à l'axe de rotation défini dans le joint.
* **Mesh filename** : Le chemin d'accès au fichier 3D exporté en collada. Ici il est possible de définir un chemin relatif mais cela peut engendrer des erreurs et que le fichier dae ne soit pas trouvé lors de l'utilisation du fichier URDF dans ROS2. Il est donc préférable d'utiliser un chemin absolu.

