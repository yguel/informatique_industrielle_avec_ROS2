.. _create_ci_for_tests:

###########################################################
Exécuter les tests automatiquement : l'intégration continue
###########################################################

.. index:: intégration continue, CI, GitHub Actions, Docker

Une suite de tests n'a de valeur que si elle est **effectivement exécutée**.
Or un test lancé à la main est un test qu'on oublie de lancer : le jour où l'on est pressé, où l'on « ne touche qu'à un détail », ou simplement sur la machine d'un collègue dont l'environnement diffère du nôtre.

L'**intégration continue** (*Continuous Integration*, CI) consiste à faire exécuter la suite de tests par un serveur, automatiquement, à chaque modification publiée du code.
Cette section montre comment le projet 5 barres s'y prend, et pourquoi chacun de ses choix est fait.

.. note::

   Vous avez déjà mis en place une CI dans :doc:`../c01_create_and_publish_doc/p01s05_www_doc` : la publication automatique de la documentation sur GitHub Pages.
   Le mécanisme est le même (un *workflow* GitHub Actions) ; ce qui change ici est l'objet du contrôle — non plus produire un site, mais **rendre un verdict** sur le code.

*******************************
Ce que la CI apporte réellement
*******************************

#. **Elle exécute les tests, systématiquement.** C'est la raison première, et elle suffirait.
#. **Elle les exécute dans un environnement propre.** Votre machine contient des paquets installés il y a six mois, des variables d'environnement oubliées et un espace de travail à moitié compilé. La CI part d'une base vierge à chaque fois, et détecte donc les dépendances que vous avez oublié de déclarer — l'erreur la plus courante et la plus pénible dans un projet ROS.
#. **Elle rend le verdict public.** Sur une *pull request* (voir :doc:`../c01_create_and_publish_doc/p01s06_cooperate_by_pull_request`), le relecteur voit immédiatement si la contribution casse quelque chose, sans avoir à récupérer la branche et à la compiler. La discussion peut alors porter sur le fond.
#. **Elle date les régressions.** Un historique de CI indique le commit exact à partir duquel un test a commencé à échouer, ce qui transforme une enquête en une simple lecture.
#. **Elle protège la branche principale.** On peut configurer GitHub pour interdire la fusion d'une branche dont la CI est rouge, ce qui garantit qu'une branche officielle reste toujours compilable et testée.

.. important::

   Pour que ces promesses tiennent, une règle de discipline prime sur toute considération technique : **une CI rouge est un problème que l'on traite immédiatement**.
   Une équipe qui s'habitue à voir du rouge perd en quelques semaines tout le bénéfice de son investissement, et il ne lui reste qu'une facture de temps de calcul.
   C'est aussi pourquoi il faut à tout prix éliminer les tests instables (*flaky*) évoqués dans :doc:`p03s02_write_tests_with_gtest`.

***************************************************
Première condition : un environnement reproductible
***************************************************

.. index:: Docker, image Docker, reproductibilité

Le problème que Docker résout
==============================

Les tests du projet ont besoin de ROS 2 Jazzy, de MuJoCo (en Python **et** en C), de Google Test, de ``ros2_control``, de ``xacro``…
Installer cela « à la main » sur le serveur de CI serait long, fragile et non reproductible : la version installée dépendrait du jour de l'installation.

C'est précisément le problème que résout une **image Docker** : une description exécutable d'un système complet, qui donne le même environnement sur le serveur de CI, sur votre machine, et sur celle de votre collègue — quelle que soit la distribution qu'il utilise.

.. literalinclude:: resources/code/five_bars/ci/Dockerfile
   :language: docker
   :caption: ``docker/Dockerfile``

Lisons-le à la lumière de ce qui précède.

Trois étages, pour trois usages
================================

Le fichier définit une image en plusieurs étapes (*multi-stage build*), chaque étape prolongeant la précédente :

.. list-table::
   :header-rows: 1
   :widths: 16 22 62

   * - Étage
     - Usage
     - Contenu
   * - ``base``
     - commun
     - ROS 2, compilateur, Google Test, MuJoCo, dépendances système. **Aucune** dépendance graphique lourde.
   * - ``ci``
     - tests, CI
     - ``base`` + les sources copiées et **déjà compilées**. Entièrement headless.
   * - ``desktop``
     - développement
     - ``ci`` + RViz, outils ``rqt`` et bibliothèques de conversion CAO.

Ce découpage n'est pas une coquetterie. L'image de CI ne contient ni RViz ni serveur X : elle est donc **plus petite, plus rapide à construire et plus rapide à télécharger**, ce qui compte quand elle est reconstruite à chaque ``push``.
C'est la contrepartie directe du choix de tests *headless* expliqué dans :doc:`p03s04_use_simulation_to_write_tests` : parce que les tests n'ont pas besoin d'affichage, la CI n'a pas besoin d'en installer.

Figer les versions
===================

Deux lignes méritent une attention particulière :

.. literalinclude:: resources/code/five_bars/ci/Dockerfile
   :language: docker
   :lines: 12-17
   :emphasize-lines: 1, 6

La version de MuJoCo est **épinglée** (``MUJOCO_VERSION=4.0.1``), et la distribution ROS aussi.
Sans cela, une mise à jour de MuJoCo publiée un mardi matin pourrait faire échouer la CI d'un code que personne n'a modifié — l'un des échecs les plus déroutants qui soient, parce que rien dans l'historique du projet ne l'explique.

.. tip::

   Épingler les versions a une contrepartie : il faut les mettre à jour volontairement, de temps en temps, dans un commit dédié dont c'est le seul objet.
   Un tel commit a un énorme avantage : si la CI devient rouge, on sait **exactement** pourquoi, et on peut revenir en arrière en une commande.

Une seule version de MuJoCo pour les deux langages
===================================================

La façon dont MuJoCo est installé mérite d'être soulignée :

.. literalinclude:: resources/code/five_bars/ci/Dockerfile
   :language: docker
   :lines: 34-41

L'installation se fait par ``pip``, et la roue Python embarque **à la fois** le module Python et la bibliothèque C (``include/`` et ``libmujoco.so.X.Y.Z``).
Le ``ln -s`` et la ligne ``ld.so.conf.d`` rendent cette bibliothèque visible au compilateur et à l'éditeur de liens, et c'est elle que ``cmake/FindMuJoCo.cmake`` (voir :doc:`p03s02_write_tests_with_gtest`) retrouve.

Conséquence : les tests C++ et les tests Python sont jugés par **exactement la même version** de l'oracle.
C'est indispensable pour que la comparaison entre les deux implémentations, évoquée dans :doc:`p03s03_write_tests_for_python`, soit interprétable.

Notez aussi les deux dernières lignes de cette commande : elles **vérifient** que l'installation a réussi (le module s'importe, les fichiers attendus existent).
Une image Docker qui échoue à la construction est un problème facile ; une image qui se construit en étant subtilement incomplète est un problème coûteux.

Le point d'entrée
==================

.. literalinclude:: resources/code/five_bars/ci/entrypoint.sh
   :language: bash
   :caption: ``docker/entrypoint.sh``

Ce petit script garantit que **toute** commande lancée dans le conteneur dispose d'un environnement ROS initialisé — ce que l'on oublie une fois sur deux à la main, avec des messages d'erreur peu explicites à la clé.

*******************************************
Le workflow GitHub Actions
*******************************************

.. index:: workflow, GitHub Actions

Voici le fichier qui décrit ce que fait le serveur à chaque modification :

.. literalinclude:: resources/code/five_bars/ci/ci.yml
   :language: yaml
   :caption: ``.github/workflows/ci.yml``

Quand la CI se déclenche
=========================

.. literalinclude:: resources/code/five_bars/ci/ci.yml
   :language: yaml
   :lines: 3-6

* ``push`` : à chaque publication de commits, **sur toutes les branches**. C'est ce qui permet de travailler sur une branche en sachant en permanence où l'on en est.
* ``pull_request`` : à chaque ouverture ou mise à jour d'une demande de fusion.
* ``workflow_dispatch`` : ajoute un bouton pour lancer la CI à la main depuis l'interface de GitHub, ce qui est précieux pour vérifier qu'un échec était bien dû à une cause extérieure.

Les permissions
================

.. literalinclude:: resources/code/five_bars/ci/ci.yml
   :language: yaml
   :lines: 8-11

Le *workflow* ne demande que ce dont il a besoin : lire le code, écrire un rapport de test et commenter une *pull request*.
C'est l'application du **principe de moindre privilège** : un *workflow* qui n'a pas le droit d'écrire dans le dépôt ne peut pas le casser, même si l'une des actions qu'il utilise se révélait malveillante.

Les étapes
===========

**1. Récupérer le code et préparer le constructeur d'images.**

.. literalinclude:: resources/code/five_bars/ci/ci.yml
   :language: yaml
   :lines: 17-19

**2. Construire l'image, ce qui compile le workspace.**

.. literalinclude:: resources/code/five_bars/ci/ci.yml
   :language: yaml
   :lines: 21-30
   :emphasize-lines: 6, 9-10

Deux détails importants.

``target: ci`` sélectionne l'étage headless : on ne construit pas RViz pour rien.

Les lignes ``cache-from`` / ``cache-to`` mettent en cache les couches de l'image chez GitHub.
Sans elles, chaque exécution réinstallerait ROS, MuJoCo et toutes les dépendances — une dizaine de minutes à chaque ``push``.
Avec elles, seules les couches réellement modifiées sont reconstruites : comme les sources sont copiées **à la fin** du ``Dockerfile``, une modification du code ne réinstalle rien.

.. tip::

   C'est la raison pour laquelle on place dans un ``Dockerfile`` les instructions de la plus stable à la plus changeante.
   Une ligne ``COPY src`` placée en haut du fichier invaliderait le cache de tout ce qui suit, et la CI deviendrait dix fois plus lente pour un résultat identique.

**3. Exécuter les tests.**

.. literalinclude:: resources/code/five_bars/ci/ci.yml
   :language: yaml
   :lines: 32-39
   :emphasize-lines: 5, 8

Cette étape est le cœur du *workflow*, et chacun de ses morceaux a une raison d'être :

* ``--return-code-on-test-failure`` : sans cette option, ``colcon test`` renvoie un code de succès **même si des tests échouent** ! La CI serait alors verte en permanence, ce qui est le pire des cas de figure. C'est l'erreur la plus fréquente dans une CI ROS 2 ;
* ``ret=$?`` puis ``exit $ret`` : le code de retour est mémorisé **avant** les commandes suivantes, puis restitué à la fin, pour que le rapport et l'archive soient produits sans masquer le verdict ;
* ``colcon test-result --verbose`` affiche le détail des échecs dans le journal de la CI, exactement comme la commande ``ros2_view_tests`` de :doc:`p03s01_run_ros2_tests` le fait sur votre machine ;
* les fichiers XML de résultats sont copiés dans un volume partagé, pour pouvoir être exploités par les étapes suivantes.

**4. Publier un rapport lisible, et archiver les résultats.**

.. literalinclude:: resources/code/five_bars/ci/ci.yml
   :language: yaml
   :lines: 41-52
   :emphasize-lines: 2, 8

Les fichiers XML produits par ``colcon`` sont au format **JUnit**, un format d'échange compris par tous les outils d'intégration continue.
L'action ``publish-unit-test-result-action`` les transforme en un tableau lisible, directement visible sur la *pull request* : nombre de tests, lesquels ont échoué et avec quel message.
Le relecteur n'a donc pas à lire le journal brut.

Le ``if: always()`` qui précède ces deux étapes est essentiel : par défaut, une étape est ignorée si une étape précédente a échoué.
Or c'est **exactement** quand les tests échouent que l'on veut le rapport. Sans ``if: always()``, la CI ne produirait de rapport que lorsqu'il n'y a rien à signaler.

.. warning::

   Cette combinaison — ``--return-code-on-test-failure`` pour que l'échec compte, et ``if: always()`` pour que le rapport soit tout de même publié — est la partie délicate de toute CI de test.
   Une CI qui ne distingue pas « les tests ont échoué » de « la CI a échoué » ne sert à rien, et les deux erreurs symétriques (verte alors que les tests échouent, muette alors qu'ils échouent) sont faciles à commettre.

*******************************************************
Exécuter la même chose sur sa machine
*******************************************************

C'est la propriété la plus utile du dispositif, et celle qu'il faut rechercher dans tout projet : **la CI ne fait rien que vous ne puissiez reproduire à l'identique chez vous**.

.. literalinclude:: resources/code/five_bars/ci/docker-compose.yml
   :language: yaml
   :caption: ``docker/docker-compose.yml``

Le service ``test`` est l'équivalent exact de la CI : **même étage d'image** (``target: ci``), mêmes options de ``colcon test``, y compris le ``--return-code-on-test-failure`` qui donne son sens au verdict.
La seule différence est qu'il recompile le workspace au démarrage, puisque les sources sont montées depuis votre machine au lieu d'être figées dans l'image.

.. code-block:: bash

   # depuis la racine du workspace
   docker compose -f docker/docker-compose.yml run --rm test

Le projet fournit également un script d'enrobage plus commode, qui construit l'image si elle manque :

.. code-block:: bash

   docker/start.sh test      # compile, puis lance tous les tests, headless
   docker/start.sh           # un shell dans le conteneur, workspace compilé
   docker/start.sh --rebuild # forcer la reconstruction de l'image

.. note::

   ``docker/start.sh test`` utilise l'image de développement (``desktop``) et non l'étage ``ci``, et appelle ``colcon test`` sans ``--return-code-on-test-failure`` : il affiche donc le détail des tests, mais son code de retour ne reflète pas leur verdict.
   C'est le bon outil pour **travailler** ; pour vérifier exactement ce que dira la CI, utilisez le service ``test`` de ``docker compose``.

.. dropdown:: ``docker/start.sh``

   .. literalinclude:: resources/code/five_bars/ci/start.sh
      :language: bash
      :caption: docker/start.sh

Deux différences entre les services ``dev`` et ``test`` du fichier ``compose`` méritent d'être relevées :

* ``dev`` monte le serveur graphique X11 et le périphérique ``/dev/dri`` pour afficher le *viewer* MuJoCo et RViz ; ``test`` n'en a pas besoin, puisque les tests sont headless ;
* dans les deux cas, ``../src`` est **monté** dans le conteneur plutôt que copié : vous éditez le code sur votre machine, avec votre éditeur, et vous le compilez dans le conteneur.

.. important::

   « Ça marche chez moi » cesse d'être un argument dès lors que vous pouvez lancer, en une commande, exactement ce que lance la CI.
   Avant d'ouvrir une *pull request*, exécutez ``docker/start.sh test`` : c'est le même verdict, obtenu quelques minutes plus tôt, et sans mobiliser le serveur.

**************************************************************
Le cas particulier de ce projet : une CI rouge, volontairement
**************************************************************

Rappelons l'état dans lequel le projet est livré : les tests existent, le code ne l'est pas, **la CI est donc rouge**.

Ce n'est pas une anomalie, c'est la traduction en CI du cycle TDD décrit dans :doc:`p03s02_write_tests_with_gtest`.
La CI y gagne un rôle supplémentaire, celui de **tableau d'avancement** : le rapport de tests publié à chaque ``push`` indique précisément combien de tests passent, et lesquels.
Votre travail consiste à faire passer la CI du rouge au vert, et vous en mesurez l'avancement sans avoir à y penser.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - État attendu
     - Interprétation
   * - 2 tests verts (banc de test), 8 rouges
     - Point de départ : l'environnement et l'oracle fonctionnent, rien n'est implémenté.
   * - Les tests ``SimulationHarness`` rouges
     - **Anomalie** : problème d'environnement, de modèle MJCF ou de géométrie. À traiter en priorité, avant toute implémentation.
   * - ``ForwardKinematics`` verts, ``InverseKinematics`` rouges
     - Avancement normal : le modèle direct est fait, le modèle inverse reste à écrire.
   * - Tous verts
     - Les deux modèles sont conformes à la spécification, dans les deux langages.

.. caution::

   Un projet dont la CI est durablement rouge est un projet où plus personne ne lit la CI.
   Tant que cet état est **volontaire et documenté** — c'est le cas ici, le ``README`` du projet l'annonce — il est acceptable.
   Dans un projet en production, la règle est l'inverse : la branche principale doit toujours être verte, et le travail en cours se fait sur une branche.

******************************************
Compléter la CI
******************************************

Protéger la branche principale
===============================

Une CI qui rend un verdict que l'on peut ignorer n'est qu'une indication.
Dans les réglages GitHub du dépôt (*Settings → Branches → Branch protection rules*), on peut exiger que la CI soit verte pour autoriser la fusion d'une *pull request*.
C'est le complément naturel de la méthodologie de contribution décrite dans :doc:`../c01_create_and_publish_doc/p01s06_cooperate_by_pull_request`.

Vérifier aussi le style
========================

Les tests de style (``flake8``, ``ament_cmake_copyright``, formatage C++) sont exécutés par ``colcon test`` au même titre que les autres : la CI les contrôle donc déjà.
Pour éviter de découvrir un problème de formatage après plusieurs minutes d'attente, mieux vaut le détecter **avant** de valider le commit, avec ``pre-commit`` : voir :doc:`../c04_collaborate_with_coders/p04s10_precommit`.

La règle d'usage est la suivante : ``pre-commit`` sur votre machine pour un retour en une seconde, la CI comme filet de sécurité qui ne peut pas être contourné.

Quelques extensions utiles
===========================

#. **Une matrice de distributions** : faire tourner le même *workflow* sur Humble et Jazzy, grâce à l'argument ``ROS_DISTRO`` déjà prévu dans le ``Dockerfile``.
#. **La couverture de code** (``lcov`` pour le C++, ``coverage`` pour Python) : elle indique quelles lignes ne sont exécutées par aucun test. À lire comme un indicateur de ce qui n'est pas testé, et non comme une note à maximiser.
#. **Un délai maximal** sur le *job* (``timeout-minutes``), pour qu'un test bloqué n'occupe pas un serveur pendant des heures.
#. **Une exécution planifiée** (``schedule``) : lancer la CI chaque nuit détecte les ruptures venues de l'extérieur, sur un code que personne n'a modifié.

*************
Exercices
*************

#. **Reproduire la CI localement.** Lancez ``docker compose -f docker/docker-compose.yml run --rm test``. Comparez le nombre de tests passés et échoués avec ce qu'annonce le rapport de la CI sur GitHub. Les deux doivent coïncider : si ce n'est pas le cas, qu'est-ce que cela révèle ?
#. **Casser le verdict.** Enlevez ``--return-code-on-test-failure`` du *workflow*, poussez la modification et observez. La CI est-elle verte ou rouge ? Combien de tests échouent réellement ? Pourquoi est-ce la panne la plus grave possible pour une CI ?
#. **Supprimer le rapport.** Enlevez les deux ``if: always()`` et poussez. Que devient le rapport de tests quand les tests échouent ? Que reste-t-il pour diagnostiquer ?
#. **Mesurer le cache.** Relevez la durée de l'étape de construction de l'image lors de deux exécutions successives, la seconde ne modifiant qu'un commentaire dans un fichier source. Expliquez l'écart. Que se passerait-il si la ligne ``COPY src /ws/src`` était placée juste après le ``FROM`` de l'étage ``base`` ?
#. **Épingler, ou pas.** Remplacez ``MUJOCO_VERSION=4.0.1`` par la dernière version disponible. Les tests passent-ils toujours ? Quel est l'intérêt, et quel est le risque, de ne pas épingler cette version ?
#. **Faire verdir la CI.** Implémentez le modèle géométrique direct, dans les deux langages, et poussez sur une branche. Combien de tests deviennent verts ? Le rapport publié par la CI correspond-il à ce que vous attendiez ?
