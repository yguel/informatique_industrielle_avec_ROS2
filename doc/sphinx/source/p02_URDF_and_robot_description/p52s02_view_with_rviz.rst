#######################
Visualisation du modèle
#######################

Il est possible de visualiser le modèle issu du fichier URDF du pantographe à l'aide de RViz. Cet outil peut être utilisé pour vérifier la validité du modèle lui-même, c'est pourquoi nous l'avons exposé au travers d'une launch file qui traite automatiquement le fichier contenant les macros Xacro. Cette approche est destinée au développement ; ainsi en production, il faudra utiliser le fichier URDF généré pour éviter le gaspillage de ressources.

Pour lancer la visualisation, utilisez la commande suivante :

.. code-block:: bash

   ros2 launch pantographe_description display.launch.py

Vous pouvez ainsi vous assurer du bon placement des repères et d'autres paramètres.
