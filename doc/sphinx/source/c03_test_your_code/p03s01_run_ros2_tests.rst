############################################
Lancer les tests de ROS2 et les analyser
############################################

Avec les commandes bash enregistrées dans ::doc:`votre fichier .bashrc <../c02_first_ros2_project_pimped/p02s01_pimped_pubsub>` , vous pouvez lancer les tests de ROS2 avec les commandes décrites ci-dessous. 
N'oubliez pas que pour que cela fonctionne, il faut avoir initialisé l'environnement ros2 et que toutes les paquets aient été compilés avec succès.

.. code-block:: bash

    ros2_humble
    ros2_build


Lancer les tests sur tous les paquets du répertoire de travail
==============================================================

.. code-block:: bash

    ros2_test

Exemple d'exécution sans erreur
-------------------------------

.. literalinclude:: resources/ros2_test_without_errors.txt
   :language: text

Exemple d'exécution avec erreurs
--------------------------------

.. literalinclude:: resources/ros2_test_with_errors.txt
   :language: text
   :linenos:
   :emphasize-lines: 10-15, 16-21



Lancer les tests pour un paquet spécifique
==========================================

La commande est:

.. code-block:: bash

    ros2_test_only <nom_du_paquet>

Par exemple:

.. code-block:: bash

    ros2_test_only scara_velocity_supervision

Analyser les résultats des tests
================================

S'il y a une erreur, la sortie des tests telle qu'indiquée dans la sortie de la commande ``ros2_test`` ou ``ros2_test_only`` est bien souvent vide et donc inutile pour comprendre l'erreur.

Pour faire une analyse des tests, il faut utiliser la commande:

.. code-block:: bash

    ros2_view_tests

Celle-ci donne des informations uniquement pour les tests qui contiennent des erreurs.
Par exemple:

.. literalinclude:: resources/ros2_view_tests_with_errors.txt
   :language: text

En exécutant ces commandes dans un terminal de vscode, 
Il suffit de faire un ``click gauche`` avec la souris sur le lien en maintenant appuyée la touche ``Ctrl`` du clavier pour ouvrir le fichier de log des tests et voir les erreurs.

.. note::

   Nous avons défini une fonction ``ros2_view_tests_all`` qui permet de voir tous les tests, même ceux qui n'ont pas d'erreur.
   Les cas d'usage sont très rares: principalement pour débuguer les CMakeLists.txt impliquant des tests et vérifier quels tests sont executés.

En ajoutant les lignes suivantes dans le fichier de configuration de vscode, vous pouvez ouvrir les fichiers de log des tests avec la coloration syntaxique adaptée:

.. code-block:: json

   "files.associations": {
        "Test.xml": "log",
        "*.xunit.xml": "log",
        "*.gtest.xml": "log"
        },

.. note::

   Si vous avez déjà une variable ``files.associations`` définie dans votre fichier de configuration, il suffit d'ajouter les lignes ci-dessus dans la définition de cette variable.

D'autres options de configuration de vscode sont disponibles dans le fichier de configuration de vscode de ce cours, qui est très inspiré du projet git: `vscode_ros2_workspace d'athackst (Allison Thackston) <https://github.com/athackst/vscode_ros2_workspace>`_

Votre fichier de configuration de vscode peut ressembler à ceci:

.. _settings_json_vscode:
.. dropdown:: settings.json

   .. tab-set::

         .. tab-item:: Humble

            .. literalinclude:: resources/code/vscode/settings_humble.json
               :language: json
               :caption: settings.json
      
         .. tab-item:: Jazzy

            .. literalinclude:: resources/code/vscode/settings_jazzy.json
               :language: json
               :caption: settings.json

Dans le rapport de tests ci-dessous:

.. literalinclude:: resources/ros2_view_tests_with_errors.txt
   :language: text
   :linenos:
   :emphasize-lines: 1, 3

Les lignes surlignées en jaune sont des fichiers qui rassemblent les erreurs pour chaque package.
Les lignes 2 et 4 explicitent les tests qui ont échoués, dans ce cas, les tests sont des tests ``flake8`` de type formatage de code python.
Ces tests sont les moins critiques car ce ne sont pas des erreurs de tests unitaires.
Ils devront néanmoins être corrigés pour que le code soit conforme aux standards de qualité et puisse être intégré dans une branche officielle du projet.

Afin de corriger ces tests rapidement, il est possible d'utiliser une fonctionnalité de vscode qui permet d'exécuter les tests directement dans l'éditeur.

Il faut configurer des tâches dans le fichier ``.vscode/tasks.json`` du répertoire du package pour exécuter les tests.

.. dropdown:: tasks.json

   .. literalinclude:: resources/code/vscode/tasks.json
      :language: json
      :caption: tasks.json

Ce fichier est intégralement repris du projet git: `vscode_ros2_workspace d'athackst (Allison Thackston) <https://github.com/athackst/vscode_ros2_workspace>`_

Un ``linter`` est un outil qui analyse le code source pour détecter des erreurs de style, de formatage ou de bonnes pratiques. |br|
C'est très utile pour maintenir un code propre et cohérent, surtout dans des projets collaboratifs. |br|
Ainsi pour un même texte de code, tous les développeurs produiront le même code finale, la même ligne de code sera formatée de la même manière et donc il n'y aura pas de différences inutiles dans les commits. |br|
Plus d'information sur ces outils sont fournies dans le chapitre :ref:`Les outils nécessaires pour collaborer entre codeurs <collaborate_with_coders>`.

Pour exécuter une tache de linter, il suffit de taper ``Ctrl+Shift+P`` puis de taper ``Run Task`` et de sélectionner la tâche voulue.

Dans notre cas, il faut sélectionner la tâche ``flake8`` pour exécuter les tests de formatage de code python.

De manière plus générale, pour les problèmes de linter, il est possible d'exécuter la tâche ``lint all`` qui exécute tous les tests de linter.