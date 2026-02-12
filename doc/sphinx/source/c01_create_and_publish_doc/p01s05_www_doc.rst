*************************
Publier la documentation
*************************

Nous allons maintenant publier la documentation sur le web mais aussi sauvegarder notre projet sur un serveur git distant afin de le partager avec d'autres personnes.

.. note::

   Pour pouvoir partager le projet et sa documentation, il faut que le projet soit sur un serveur git distant, accessible par tout utilisateur que vous avez autorisé et tout le temps.
   Dans ce tutoriel nous allons créer un projet publique sur ``github``

Créer un compte sur github
==========================

Si vous avez déjà un compte github, vous pouvez passer à la section suivante et utiliser votre compte.

Pour créer un compte sur github, allez sur le site `github <https://github.com/>`_ et cliquez sur le bouton ``Sign up`` en haut à droite ou cliquez sur le lien: `github signup <https://github.com/signup>`_. Remplissez les informations demandées et cliquez sur le bouton ``Create account``.

Créer un dépôt sur github
=========================

Une fois connecté sur github, vous pouvez créer un nouveau dépôt en cliquant sur le bouton ``New`` en haut à droite ou en cliquant sur le lien: `github new repository <https://github.com/new>`_.

Remplissez les informations demandées:
et appelez votre dépôt ``info_indus_tutorial``.


Créer une clé ssh et l'ajouter à github
---------------------------------------

Pour pouvoir pousser votre projet sur github, il est recommandé d'utiliser une clé ssh. Pour créer une clé ssh, ouvrez un terminal et tapez la commande suivante:

.. code-block:: bash

   ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519_info_indus_tutorial

Remplacez ``your_email@example.com`` par votre email.

Maintenant vous allez ajouter la clé ssh à votre compte github. Pour cela, copiez le contenu de la clé publique dans le presse-papier:

.. code-block:: bash

   cat ~/.ssh/id_ed25519_info_indus_tutorial.pub

Allez sur la page de votre compte github et cliquez sur votre photo de profil en haut à droite, puis cliquez sur ``Settings``. Dans la colonne de gauche, cliquez sur ``SSH and GPG keys`` et enfin sur le bouton ``New SSH key``. Collez le contenu de la clé publique dans le champ ``Key`` et cliquez sur le bouton ``Add SSH key``.


Vous pouvez maintenant ajouter votre clé à l'agent ssh, cela vous évitera de taper votre mot de passe à chaque fois que vous poussez sur github:

.. code-block:: bash

   ssh-agent /bin/bash

.. code-block:: bash
      
   ssh-add ~/.ssh/id_ed25519_info_indus_tutorial




Poussez le projet sur github
============================

Pour pousser le projet sur github, il faut ajouter le dépôt distant à votre dépôt local et pousser les modifications.

Pour trouver l'adresse du dépôt distant à utiliser pour pousser votre projet, allez sur la page de votre dépôt github et copiez l'adresse du dépôt.

Vous avez besoin de l'adresse ssh du dépôt (voir la procédure pas à pas). La procédure animée montre quant-à-elle la procédure pour obtenir l'adresse https du dépôt. Elles sont identiques jusqu'au moment où vous choisissez le type d'adresse du dépôt à copier.

L'adresse ssh vous permet de pousser sans taper de mot de passe tandis qu'avec l'adresse https vous serez forcés d'entrer votre mot de passe à chaque fois que vous poussez. Par contre, comme le dépôt est public, vous pouvez utiliser l'adresse https sans aucune configuration pour copier le dépôt (le cloner) nous verrons plus loin où cela peut être utile.

.. index:: 
   git; remote
   git; adresse du dépôt distant
   github; remote
   github; adresse du dépôt distant

Trouver l'adresse du dépôt distant pour les opérations de clone, pull, push, etc.

.. _get_git_remote_project_address:
.. tabs::

   .. tab:: Procédure animée (https)

      .. figure:: resources/img/access_https_git_clone_address.gif
         :align: center
         :width: 80%

   .. tab:: Procédure pas à pas (ssh)

      .. figure:: resources/img/get_git_remote_project_address_01.png
         :align: center
         :width: 80%

      .. figure:: resources/img/get_git_remote_project_address_02.png
         :align: center
         :width: 80%

      .. figure:: resources/img/get_git_remote_project_address_03.png
         :align: center
         :width: 80%

.. code-block:: bash

   git remote add origin MY_GIT_REMOTE_ADDRESS

Remplacez ``MY_GIT_REMOTE_ADDRESS`` par l'adresse du dépôt distant que vous venez de copier.

.. note:: Il y a une autre manière de récupérer l'adresse du dépôt gihub utilisable pour les opérations de clone, pull, push, etc. C'est en utilisant la commande suivante: ``git remote get-url origin`` . D'un point de vue mémo-techique, j'utilise une commande plus simple: ``git remote -v`` qui me donne l'adresse des dépôts distants et leur nom (``origin`` est celui qui nous intéresse ici). Cette commande est plus simple à retenir pour 2 raisons en plus d'être plus courte: 1) ``remote`` design le dépôt distant, 2) ``-v`` pour verbose, c'est-à-dire afficher les informations de manière détaillée, c'est l'option courante dans le monde des commandes linux pour obtenir plus d'informations.

Changement de nom de la branche principale
------------------------------------------
Effectuez les commandes suivantes:

.. code-block:: bash
   
   git branch -a
   git branch -M rolling
   git branch -a

The branch commands permet de renommer la branche principale (appelée main ou master) en ``rolling`` en accord avec la politique de nommage de ROS2.

Pousser le code sur github
--------------------------

Voyons maintenant la commande pour pousser le code sur github:

.. code-block:: bash

   git push -u origin rolling

C'est seulement la première fois que vous poussez une branche sur un dépôt distant que vous devez utiliser l'option ``-u remote_reopsitory local branch``. Cette option définit la branche en amont pour la branche que vous poussez. Après cela, vous pouvez utiliser ``git push`` sans l'option ``-u``.

Maintenant vous pouvez aller sur la page de votre dépôt github et rafraîchir la page.
Vous devriez voir les fichiers de votre projet s'afficher sur github.

Créer le workflow git et voir la documentation apparaître sur le web en temps réel
===================================================================================



Regarder les branches existantes:

.. code-block:: bash

   git branch -a

Créer la branche ``gh-pages`` vide:

.. code-block:: bash

   git switch --orphan gh-pages

.. code-block:: bash

   git branch -a

Créer un fichier sur cette branche nommée ``.gitkeep`` cela permet de garder le répertoire vide et de pouvoir pousser la branche sur github:

.. code-block:: bash

   touch .gitkeep
   git add .gitkeep
   git commit -m "First commit of the gh-pages branch"
   git push -u origin gh-pages
   git checkout rolling

Nous allons créer un fichier spécial qui va dire à github de créer et de publier la documentation à chaque fois qu'un changement est fait sur la branche rolling

Créer le fichier ``.github/workflows/documentation.yml`` à la racine du projet git:

.. code-block:: bash

   mkdir -p .github/workflows
   touch .github/workflows/documentation.yml

Ajouter le contenu suivant dans le fichier ``.github/workflows/documentation.yml``:

.. _github_workflow_doc:
.. literalinclude:: ../../../../.github/workflows/documentation.yml
   :language: yaml
   :caption: Fichier de CI (action de workflow github) documentation.yml
   :linenos:
   :emphasize-lines: 40 

Modifiez la ligne surlignée du fichier de workflow commençant par ``git clone ...``, pour que dans le workflow ce soit bien votre projet qui soit téléchargé. Remplacez ``https://github.com/yguel/informatique_industrielle_avec_ROS2.git`` par l'adresse ``HTTPS`` de votre dépôt github (MY_GIT_REMOTE_ADDRESS que vous pouvez récupérer en suivant la :ref:`procédure ci-dessus <get_git_remote_project_address>` (procédure pas-à-pas). Nous utilisons ici, l'adresse ``HTTPS`` pour que le workflow n'est pas besoin de code d'accès pour cloner le dépôt. Comme le dépôt est publique c'est la méthode d'accès la plus simple pour le workflow.

Par contre pour modifier le dépôt: action ``push``, il faut forcément des autorisations car le dépôt n'est pas en écriture pour tout le monde. C'est pour cela que dans le ::ref:` workflow<github_workflow_doc>`, l'action ``Push changes`` lignes 49-54, a un champ particulier ``github_token`` qui permet d'authentifier le workflow pour qu'il puisse pousser les modifications sur le dépôt. Le mot de passe est généré automatiquement par GitHub, et les actions github auront le droit de pousser sur le dépôt une fois que vous aurez fait :ref:`les modifications dans les settings du projet ci-après<setup_git_actions>`.




Il faut maintenant faire quelques modifications dans les settings du projet sur github
Il faut:

#. aller dans les settings du projet
#. aller dans la section ``Actions``
#. aller dans la sous-section ``General``
#. cocher les 3 cases :

   #. ``Allow all actions and reusable worflows`` (normalement ok par défaut)
   #. Dans la section ``Workflow permissions`` cocher 

     #. ``Read and write permissions``
     #. ``Allow GitHub Actions to create and approve pull requests``
   
.. _setup_git_actions:
.. figure:: resources/img/setup_git_actions_01.png
   :align: center
   :width: 80%

.. figure:: resources/img/setup_git_actions_02.png
   :align: center
   :width: 80%

.. figure:: resources/img/setup_git_actions_03.png
   :align: center
   :width: 80%

.. figure:: resources/img/setup_git_actions_04.png
   :align: center
   :width: 80%

Maintenant vous pouvez ajouter le fichier de workflow à git et pusher:

.. code-block:: bash

   git add .github/workflows/documentation.yml
   git commit -m "Add github action to build and publish the documentation"
   git push

Maintenant, vous pouvez voir la documentation apparaître sur le web en temps réel en allant sur la page de votre dépôt github et en cliquant sur le lien ``Actions``.

Vous avez peut-être besoin de faire un nouveau commit pour que le workflow se déclenche.

Petit exercice: modifiez le fichier ``doc/sphinx/source/index.rst`` et ajoutez une ligne de texte. Poussez les modifications sur github à l'aide des commandes git : ``add, commit puis push`` et regardez la documentation se mettre à jour en temps réel.

Allez sur l'onglet ``Actions`` de votre dépôt github pour voir le workflow se déclencher et construire la documentation, vous pouvez suivre en temps réel ce qui se passe et notamment voir les logs ou les erreurs s'il y en a.

.. _workflow_in_action:
.. figure:: resources/img/workflow_in_action.gif
   :align: center
   :width: 80%
