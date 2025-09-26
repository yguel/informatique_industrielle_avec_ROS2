**********************************************
Création d'une première documentation sphinx
**********************************************

=======================
Installer sphinx
=======================

.. code-block:: bash
   
   sudo apt-get update

.. code-block:: bash

   sudo apt-get install -f python3-sphinx

Créer un répertoire pour la documentation:

.. code-block:: bash

   mkdir -p doc/sphinx

Créer un fichier requirments.txt pour les dépendances de la documentation:

.. code-block:: bash

   touch ~/info_indus/info_indus_tutorial/doc/sphinx/requirements.txt

Ajouter les dépendances suivantes dans le fichier ``requirements.txt`` avec vscode:

.. literalinclude:: ../../requirements.txt

Installer les dépendances:

.. code-block:: bash

   cd ~/info_indus/info_indus_tutorial/doc/sphinx

.. code-block:: bash

   python3 -m venv .venv

.. code-block:: bash

   source .venv/bin/activate

.. code-block:: bash

   pip install -r requirements.txt


============================
Configurer la documentation
============================

Initialiser la documentation avec les outils sphinx:

.. code-block:: bash

   cd ~/info_indus/info_indus_tutorial/doc

.. code-block:: bash

   sphinx-quickstart sphinx

Répondre aux questions posées par sphinx-quickstart.

------------------------
Séparation source/build
------------------------
Il est judicieux de séparer les sources du répertoire de build car du point de vue de la sauvegarde et du versionnement du projet avec git, on peut suivre tout ce qui se trouve dans le répertoire ``source``.
On ne versionne en effet pas le répertoire de build, car il contient des éléments générés automatiquement donc qui peuvent être intégralement déduits de tous les autres fichiers versionnés.
On gagne ainsi beaucoup en quantité de données versionnées, c'est donc un gain de resources de temps de calcul et d'espace mémoire. 

--------------
Nom du projet
--------------
Pour le nom du projet, il faut choisir un nom le plus court possible et qui soit aussi représentatif que possible du projet et de son usage.
Il est courant, par exemple, de préfixer une librairie python avec le préfix ``py``.

Pour ce projet, la règle que nous allons choisir est la suivante: utilisez les initiales des personnes de votre groupe suivi de ``info_indus_tutorial``. Par exemple, pour le groupe d' Amélie POULAIN, Jean DUPONT et Nikita TESTU, le nom du projet sera ``PaDjTn_info_indus_tutorial``.

-------------------------------------------------------------------------
Examiner les fichiers créés par sphinx-quickstart du point de vue de git
-------------------------------------------------------------------------

Regarder avec git les nouveaux fichiers créés:

.. code-block:: bash

   git status



-----------------------------------------------
Éditer les fichiers de configuration de sphinx
-----------------------------------------------

Modifier le fichier ``conf.py``:

1. mettre-à-jour les extensions,
2. mettre-à-jour le theme html de la documentation (:code:`html_theme`),
3. donner les options pour l'extension copybutton,
4. donner le chemin du fichier css

.. literalinclude:: ../conf.py
   :language: python
   :caption: Fichier de configuration de Sphinx (et oui! c'est du python)
   :linenos:
   :emphasize-lines: 33-41,65,67-69,76-78

Ajouter les fichiers créés par sphinx-quickstart:

Ajouter le fichier ``custom.css`` dans le répertoire ``_static/css``:

.. code-block:: bash

   mkdir -p ~/info_indus/info_indus_tutorial/doc/sphinx/source/_static/css

.. code-block:: bash

   touch ~/info_indus/info_indus_tutorial/doc/sphinx/source/_static/css/custom.css

.. literalinclude:: ../_static/css/custom.css
   :language: css
   :caption: Fichier css custom.css
   :linenos:


=======================
Créer la documentation
=======================

Depuis le répertoire ``sphinx`` faire:

.. code-block:: bash

   cd ~/info_indus/info_indus_tutorial/doc/sphinx

.. code-block:: bash

   make html

La documentation est un site statique html qui se trouve dans le répertoire ``build/html``.
Le fichier ``index.html`` est la page d'accueil de la documentation.
Ouvrir la documentation avec un navigateur web, par exemple firefox:

.. code-block:: bash

   firefox ~/info_indus/info_indus_tutorial/doc/sphinx/build/html/index.html

=======================================
Sauvegarder la documentation avec git
=======================================

Voir l'état de votre dépôt git:

.. code-block:: bash

   git status

Ajouter les fichiers de la documentation:

.. code-block:: bash

   cd ~/info_indus/info_indus_tutorial/doc/sphinx

.. code-block:: bash

   git add source

.. code-block:: bash
   
   git add Makefile make.bat requirements.txt

Fair le commit des modifications:

.. code-block:: bash

   git commit -m "First commit of the documentation"
   