*************************************
Introduction au versionning avec git
*************************************

Git est un logiciel de gestion de versions décentralisé. C'est un logiciel libre créé par Linus Torvalds, le créateur de Linux. Il permet de suivre l'évolution d'un projet informatique en enregistrant les différentes versions des fichiers qui le composent. Git est très utilisé dans le monde du développement logiciel, mais il peut également être utilisé pour suivre l'évolution de tout type de fichier.

.. note::

   Git est un logiciel en ligne de commande. Il existe des interfaces graphiques pour Git, mais il est recommandé de commencer par apprendre à utiliser Git en ligne de commande.

À la racine de votre projet (``cd ~/info_indus/info_indus_tutorial``), initialisez un dépôt git en tapant la commande suivante:

.. code-block:: bash

   git init

Cela crée un répertoire caché ``.git`` à la racine de votre projet. Ce répertoire contient toutes les informations nécessaires pour gérer les versions de votre projet.

.. note::

   Il est important de ne pas supprimer ou modifier le répertoire ``.git``. Cela pourrait corrompre votre dépôt git.

Pour voir l'état de votre dépôt git, tapez la commande suivante:

.. code-block:: bash

   git status

Nous voyons que notre répertoire ``.vscode`` apparaît en rouge dans la section ``Untracked files``. Cela signifie que git ne suit pas les modifications de ce répertoire.

Nous emploierons souvent cette commande pour voir l'état de notre dépôt git.

Nous allons ajouter le répertoire ``.vscode`` à notre dépôt git. Pour cela, tapez la commande suivante:

.. code-block:: bash

   git add .vscode

Le répertoire ainsi que les fichiers qu'il contient sont maintenant suivis par git.
Nous pouvons voir l'état de notre dépôt git en tapant la commande suivante:

.. code-block:: bash

   git status

Nous voyons que le répertoire ``.vscode`` est ajouté par git, mais il n'est pas encore enregistré dans l'historique de git.

Pour enregistrer ces modifications dans l'historique de git, tapez la commande suivante:

.. code-block:: bash

   git commit -m "First commit"

Git ne doit pas être configuré et il vous demande de mettre des variables à jour. Faites le en suivant les instructions.

.. code-block:: bash

   git config user.email "mon.email@insa-strasbourg.fr"

.. code-block:: bash
   
   git config user.name "Prénom NOM"


.. note::

   L'option ``--global`` est pour que ces informations soient utilisées pour tous les projets git de votre machine, comme les machines sont partagées, il est préférable de ne pas mettre ces informations globalement, mais par projet.

Maintenant votre premier commit devrait fonctionner:

.. code-block:: bash

   git commit -m "First commit"

Cela enregistre les modifications dans l'historique de git avec le message ``First commit``.

On peut voir l'historique des commits en tapant la commande suivante:

.. code-block:: bash

   git log