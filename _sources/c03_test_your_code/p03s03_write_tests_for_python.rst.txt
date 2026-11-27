.. _write_tests_for_python:

####################################
Écrire des tests pour du code Python
####################################

.. index:: unittest, pytest, test unitaire Python

Le projet support du chapitre demande d'écrire le **même** modèle géométrique deux fois : une fois en C++, une fois en Python.
Les tests sont donc eux aussi écrits deux fois, et cela tombe bien : comparer les deux suites est la façon la plus rapide de comprendre ce qui, dans un test, relève du principe et ce qui relève de l'outil.

Cette section suppose la lecture de :doc:`p03s02_write_tests_with_gtest`, dont elle reprend le vocabulaire (cas de test, fixture, tolérance, invariant, oracle) sans le redéfinir.

Le code à écrire côté Python est le pendant exact du code C++ :

.. literalinclude:: resources/code/five_bars/kinematics/src/kinematics.py
   :language: python
   :pyobject: Geometry
   :caption: ``five_bars_kinematics/five_bars_kinematics/kinematics.py`` — les paramètres géométriques

.. literalinclude:: resources/code/five_bars/kinematics/src/kinematics.py
   :language: python
   :pyobject: forward_kinematics
   :caption: La fonction à implémenter, avec son contrat

Notez que le contrat est écrit **dans la docstring** : unités, repère, valeur de retour, et surtout le cas d'échec (``None``).
C'est la spécification que les tests vont vérifier, et elle est écrite à l'endroit où le développeur la lira : dans le code lui-même.

*************************************************
``unittest`` ou ``pytest`` : lequel utiliser ?
*************************************************

Deux outils coexistent dans l'écosystème Python, et tous deux sont utilisés par ROS 2.

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * -
     - ``unittest``
     - ``pytest``
   * - Origine
     - bibliothèque standard de Python
     - paquet externe (``python3-pytest``)
   * - Écriture d'un test
     - une méthode ``test_*`` dans une classe dérivant de ``unittest.TestCase``
     - une simple fonction ``test_*``, dans ou hors d'une classe
   * - Vérifications
     - méthodes ``self.assertXxx(...)``
     - le mot-clé ``assert`` de Python, réécrit pour afficher les valeurs
   * - Contexte partagé
     - ``setUp`` / ``setUpClass``
     - *fixtures* (décorateur ``@pytest.fixture``), plus souples
   * - Exécution
     - ``python3 -m unittest``
     - ``pytest``, qui sait **aussi** exécuter les tests ``unittest``

Le point à retenir : ``pytest`` exécute les tests écrits avec ``unittest``, l'inverse n'est pas vrai.
Un test écrit en ``unittest`` est donc le choix le plus portable, et c'est celui du projet.

.. note::

   Dans ROS 2, ``pytest`` est de toute façon présent : c'est lui qui exécute les tests des paquets ``ament_python`` et qui produit les rapports XML, que les tests soient écrits dans un style ``unittest`` ou non.

*************************************
Structure d'un fichier de tests
*************************************

Le fichier de tests Python du projet suit la même organisation que son équivalent C++ : une classe de base qui prépare le contexte, puis une classe par sujet.

Préparer le contexte : ``setUpClass``
======================================

``setUpClass`` est l'équivalent de ``SetUpTestSuite`` en gtest : il est appelé **une seule fois** pour la classe, ce qui permet de ne charger qu'une fois le modèle de simulation.
``setUp``, lui, est appelé avant **chaque** méthode de test.

.. literalinclude:: resources/code/five_bars/kinematics/test/test_kinematics.py
   :language: python
   :pyobject: MujocoTestCase
   :caption: La classe de base, qui joue le rôle de la fixture C++

Comme en C++, la classe de base fournit une méthode d'aide ``simulate()`` qui amène la simulation à l'équilibre et vérifie au passage deux conditions de validité de la mesure.
Et comme en C++, les classes de test dérivent de cette classe de base au lieu de dupliquer ce code.

.. important::

   ``setUpClass`` est un ``@classmethod`` : il s'applique à la **classe**, donc les objets qu'il crée sont partagés par tous les tests de cette classe.
   Tout ce qui est partagé et **mutable** doit être remis à zéro par test — ici, c'est ``self.sim.reset()``, appelé au début de ``simulate()`` et au début des tests qui lisent l'état initial.
   C'est la même exigence d'indépendance des tests qu'en C++, avec le même piège.

Les vérifications usuelles
===========================

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Méthode
     - Usage
   * - ``assertTrue(x)`` / ``assertFalse(x)``
     - valeurs booléennes
   * - ``assertEqual(a, b)``
     - égalité exacte — **jamais pour des flottants**
   * - ``assertAlmostEqual(a, b, delta=t)``
     - égalité de flottants à ``t`` près : l'équivalent de ``EXPECT_NEAR``
   * - ``assertIsNone(x)`` / ``assertIsNotNone(x)``
     - cas d'erreur et cas nominal des fonctions qui renvoient ``None``
   * - ``assertLess(a, b)`` / ``assertGreater(a, b)``
     - comparaisons, par exemple une distance inférieure à une tolérance
   * - ``assertRaises(Erreur)``
     - vérifier qu'un appel lève bien une exception
   * - ``np.testing.assert_allclose(a, b, atol=t)``
     - comparer des **tableaux** de flottants élément par élément

.. warning::

   ``assertAlmostEqual(a, b)`` sans argument ``delta`` compare à **7 décimales près**, ce qui n'a aucun sens physique : 10\ :sup:`-7` m est un dixième de micromètre.
   Indiquez toujours explicitement ``delta=`` (ou ``atol=`` pour ``numpy``), avec la justification de sa valeur.

Les tolérances du projet sont, comme en C++, déclarées et commentées en un seul endroit, avec les mêmes valeurs :

.. literalinclude:: resources/code/five_bars/kinematics/test/test_kinematics.py
   :language: python
   :lines: 31-33
   :caption: Les tolérances, identiques à celles de la suite C++

.. tip::

   Les tolérances **doivent** être identiques dans les deux langages : les deux implémentations résolvent le même problème géométrique et sont jugées par la même référence.
   Si l'une des deux avait besoin d'une tolérance plus large pour passer, ce serait le signe d'une erreur dans cette implémentation, et non d'une particularité du langage.

Comparer des tableaux avec ``numpy``
=====================================

La position du stylo est un couple de coordonnées. ``numpy.testing.assert_allclose`` compare les deux éléments en une seule vérification et, en cas d'échec, affiche l'écart maximal et le nombre d'éléments en désaccord :

.. literalinclude:: resources/code/five_bars/kinematics/test/test_kinematics.py
   :language: python
   :pyobject: TestForwardKinematics.test_home_configuration
   :caption: Comparaison d'un couple de coordonnées à la position mesurée dans la simulation

.. caution::

   ``assert_allclose`` possède deux tolérances : ``atol`` (absolue) et ``rtol`` (relative, **0 par défaut sur** ``assert_allclose``... mais pas sur d'autres fonctions ``numpy``, où elle vaut 10\ :sup:`-7`).
   Pour des longueurs en mètres, c'est la tolérance **absolue** qui a un sens physique : on veut 0,1 mm, pas « 0,1 % de la valeur », car près de l'origine une tolérance relative devient absurde.
   Précisez donc toujours ``atol=``.

.. _python_subtest:

Boucler sur des données sans perdre le diagnostic : ``subTest``
================================================================

.. index:: subTest

C'est l'équivalent Python de ``SCOPED_TRACE``, et il est encore plus utile.
Un test qui boucle sur 16 configurations s'arrêterait à la **première** erreur, et le rapport ne dirait pas laquelle.
``subTest`` résout les deux problèmes à la fois : chaque itération est signalée séparément, et la boucle **continue** après un échec.

.. literalinclude:: resources/code/five_bars/kinematics/test/test_kinematics.py
   :language: python
   :pyobject: TestForwardKinematics.test_matches_mujoco_simulation
   :emphasize-lines: 3
   :caption: Un balayage de l'espace de travail, chaque itération étant identifiée

Les paramètres passés à ``subTest`` apparaissent dans le rapport d'échec sous la forme ``(q1_deg=90.0, q4_deg=20.0)``.
C'est ce qui explique une particularité des résultats que nous verrons plus bas : **10 tests** déclarés peuvent produire **64 erreurs**, car chaque sous-test compte.

Invariants et cas d'erreur
===========================

Les propriétés vérifiées sont exactement les mêmes qu'en C++ (voir :doc:`p03s02_write_tests_with_gtest`) : un cas nominal, un balayage, un piège à erreur connue, un invariant et les cas d'erreur.

.. literalinclude:: resources/code/five_bars/kinematics/test/test_kinematics.py
   :language: python
   :pyobject: TestInverseKinematics.test_inverse_of_forward_is_identity
   :caption: L'invariant ``IK ∘ FK = identité``

.. literalinclude:: resources/code/five_bars/kinematics/test/test_kinematics.py
   :language: python
   :pyobject: TestInverseKinematics.test_unreachable_point_returns_none
   :caption: Les cas d'erreur — avec, en première ligne, un cas valide

La première ligne de ce dernier test mérite d'être soulignée une seconde fois : sans elle, une fonction qui renverrait toujours ``None`` passerait le test.
C'est une erreur classique, et elle est d'autant plus facile à commettre en Python que rien n'oblige une fonction à renvoyer quelque chose.

Rendre un fichier de tests exécutable seul
===========================================

Les trois dernières lignes du fichier permettent de le lancer directement, sans ``colcon`` ni ``pytest`` :

.. literalinclude:: resources/code/five_bars/kinematics/test/test_kinematics.py
   :language: python
   :lines: 141-142

C'est un petit confort qui change la vie en phase de mise au point.

******************************************
Intégrer les tests Python au paquet ROS 2
******************************************

La façon de déclarer les tests dépend du type de paquet, et c'est une source d'erreurs fréquente.

Dans un paquet ``ament_cmake``
===============================

.. index:: ament_add_pytest_test

``five_bars_kinematics`` est un paquet ``ament_cmake`` (il contient du C++) qui fournit **aussi** un module Python.
Le module est installé par ``ament_python_install_package``, et les tests Python sont déclarés par ``ament_add_pytest_test`` :

.. literalinclude:: resources/code/five_bars/kinematics/CMakeLists.txt
   :language: cmake
   :lines: 23-47
   :emphasize-lines: 2, 22-24
   :caption: ``CMakeLists.txt`` — un seul paquet déclare la bibliothèque C++, le module Python et les deux suites de tests

L'option ``ENV`` passe une variable d'environnement au test.
C'est le pendant du ``target_compile_definitions`` utilisé pour le test C++ : dans les deux cas, **le chemin du modèle de simulation est fourni par le système de compilation**, et le test ne dépend donc pas du répertoire depuis lequel on le lance.

Les dépendances de test correspondantes sont déclarées dans le ``package.xml`` :

.. literalinclude:: resources/code/five_bars/kinematics/package.xml
   :language: xml
   :lines: 13-18

Dans un paquet ``ament_python``
================================

``five_bars_mujoco`` est un paquet purement Python. Il n'y a pas de ``CMakeLists.txt`` : ``colcon`` découvre automatiquement les fichiers ``test/test_*.py`` et les exécute avec ``pytest``.
Il suffit alors de déclarer la dépendance de test :

.. literalinclude:: resources/code/five_bars/mujoco/package.xml
   :language: xml
   :lines: 21
   :caption: ``five_bars_mujoco/package.xml``

et, dans ``setup.py``, l'extra correspondant :

.. literalinclude:: resources/code/five_bars/mujoco/setup.py
   :language: python
   :lines: 13-14
   :caption: ``five_bars_mujoco/setup.py``

.. list-table:: Récapitulatif
   :header-rows: 1
   :widths: 25 35 40

   * - Type de paquet
     - Déclaration des tests Python
     - Emplacement attendu
   * - ``ament_python``
     - automatique (découverte par ``colcon``)
     - ``test/test_*.py``
   * - ``ament_cmake``
     - ``ament_add_pytest_test(...)`` dans ``if(BUILD_TESTING)``
     - au choix, par convention ``test/``

.. note::

   Dans un paquet ``ament_cmake``, oublier ``ament_add_pytest_test`` est une erreur silencieuse : les tests ne sont **pas** exécutés, et ``colcon test`` affiche un succès.
   C'est exactement le genre de situation que détecte la commande ``ros2_view_tests_all`` mentionnée dans :doc:`p03s01_run_ros2_tests` : elle liste tous les tests exécutés, y compris ceux qui passent, et permet donc de vérifier que vos tests sont bien pris en compte.

Les tests de style, déjà rencontrés
====================================

.. index:: flake8, pep257, linter

Les échecs ``flake8`` analysés dans :doc:`p03s01_run_ros2_tests` sont eux aussi des tests Python, ajoutés automatiquement par ROS 2 aux paquets qui déclarent ``ament_lint_auto`` / ``ament_flake8``.
Ils ne vérifient pas le comportement du code mais son **style**.

Ce sont les moins critiques, et il ne faut pour autant pas les laisser échouer : un paquet dont les tests sont rouges pour une raison de forme masque les échecs qui comptent.
Le sujet du formatage automatique est traité dans :doc:`../c04_collaborate_with_coders/p04s01_format_your_code`, et :doc:`../c04_collaborate_with_coders/p04s10_precommit` montre comment faire corriger ces erreurs avant même de valider un commit.

*****************************
Lancer les tests Python
*****************************

Via ``colcon``, comme tous les autres tests :

.. code-block:: bash

   ros2_test_only five_bars_kinematics
   ros2_view_tests

Directement, ce qui est bien plus rapide en phase de développement :

.. code-block:: bash

   # toute la suite, en mode bavard (-v affiche le nom de chaque test)
   python3 -m unittest discover -s src/five_bars_kinematics/test -p "test_*.py" -v

   # une seule classe, ou un seul test
   python3 -m unittest -v test_kinematics.TestForwardKinematics
   python3 -m unittest -v test_kinematics.TestForwardKinematics.test_home_configuration

Ou avec ``pytest``, dont la sélection par motif est très pratique :

.. code-block:: bash

   pytest -v src/five_bars_kinematics/test/test_kinematics.py

   # ne garder que les tests dont le nom contient "pen_offset"
   pytest -v -k pen_offset src/five_bars_kinematics/test/

   # s'arrêter au premier échec, et afficher la valeur des variables locales
   pytest -x -l src/five_bars_kinematics/test/

.. important::

   Lancés à la main, hors de ``colcon``, ces tests ont besoin de savoir où sont le module à tester et le modèle de simulation.
   C'est le rôle de ``PYTHONPATH`` et de ``FIVE_BARS_MJCF`` :

   .. code-block:: bash

      export PYTHONPATH=$PWD/src/five_bars_mujoco:$PWD/src/five_bars_kinematics
      export FIVE_BARS_MJCF=$PWD/src/five_bars_description/mjcf/five_bars.xml

   Dans un espace de travail compilé, ``source install/setup.bash`` s'en charge pour ``PYTHONPATH``, et le code de localisation du modèle trouve le fichier dans le paquet installé.

*************************************
Lire et interpréter les résultats
*************************************

Les tests du banc d'essai, qui passent
=======================================

Le paquet ``five_bars_mujoco`` contient les tests de la simulation elle-même. Ils passent dès le départ :

.. literalinclude:: resources/five_bars_test_sim_ok.txt
   :language: text
   :caption: ``python3 -m unittest discover -s src/five_bars_mujoco/test -v``

Ces cinq tests ne vérifient pas le modèle géométrique : ils vérifient que la **référence** est fiable (la chaîne est fermée, la simulation suit ses consignes, les consignes hors débattement sont saturées, les configurations impossibles sont signalées).
C'est le sujet de :doc:`p03s04_use_simulation_to_write_tests`.

Les tests de cinématique, qui échouent
=======================================

Sur le projet livré, la suite de cinématique donne ceci :

.. literalinclude:: resources/five_bars_pytest_initial.txt
   :language: text
   :emphasize-lines: 7-8, 16-18, 33-35
   :caption: ``python3 -m unittest discover -s src/five_bars_kinematics/test -v``

Trois enseignements dans cette sortie.

**Le verdict porte sur la bonne cause.** Les erreurs sont des ``NotImplementedError`` levées par ``kinematics.py`` : les tests échouent parce que le code n'existe pas, et non parce qu'ils sont mal écrits.
Les deux tests de ``TestSimulationHarness`` passent, ce qui confirme que l'environnement et la référence sont corrects.

**La trace désigne la ligne fautive.** Chaque erreur donne la pile d'appels complète : la ligne du test (``test_kinematics.py``, ligne 79) **et** la ligne du code testé (``kinematics.py``, ligne 51).
C'est l'avantage principal de Python sur le C++ en phase de mise au point.

**« 10 tests, 64 erreurs » n'est pas une contradiction.** Les méthodes de test sont au nombre de 10, mais celles qui bouclent avec ``subTest`` produisent une erreur par itération : 16 configurations × plusieurs tests, plus 12 cibles, d'où 64.
Si vous voyez un nombre d'échecs supérieur au nombre de tests, c'est normal, et c'est même utile : cela signifie que vous saurez **toutes** les configurations qui posent problème, et pas seulement la première.

.. tip::

   ``NotImplementedError`` est signalé comme ``ERROR`` et non comme ``FAIL``.
   La distinction est utile : un ``FAIL`` est une vérification qui a rendu un verdict négatif, un ``ERROR`` est une exception imprévue qui a interrompu le test.
   Un ``ERROR`` inattendu dans une suite habituellement verte évoque un problème d'environnement (dépendance manquante, fichier introuvable) plutôt qu'une régression du calcul.

***********************************************
Deux langages, une seule spécification
***********************************************

Pour finir, comparons les deux suites de tests. Les mécanismes diffèrent :

.. list-table::
   :header-rows: 1
   :widths: 34 33 33

   * - Rôle
     - Google Test (C++)
     - ``unittest`` (Python)
   * - Déclarer un test
     - ``TEST_F(Suite, Nom)``
     - ``def test_nom(self)`` dans une classe
   * - Contexte partagé par la suite
     - ``SetUpTestSuite()``
     - ``setUpClass()``
   * - Contexte par test
     - ``SetUp()``
     - ``setUp()``
   * - Comparer des flottants
     - ``EXPECT_NEAR(a, b, tol)``
     - ``assertAlmostEqual(a, b, delta=tol)``
   * - Comparer des tableaux
     - boucle + ``EXPECT_NEAR``
     - ``np.testing.assert_allclose(a, b, atol=tol)``
   * - Échec non bloquant / bloquant
     - ``EXPECT_*`` / ``ASSERT_*``
     - ``assertXxx`` (non bloquant via ``subTest``) / exception
   * - Identifier une itération
     - ``SCOPED_TRACE(...)``
     - ``with self.subTest(...)``
   * - Absence de résultat
     - ``std::optional`` vide
     - ``None``

…mais les **propriétés vérifiées sont identiques** : mêmes 16 configurations, mêmes 12 cibles, mêmes tolérances, mêmes invariants, mêmes cas d'erreur, même oracle.
C'est le signe que la spécification a été pensée indépendamment du langage, et c'est le véritable enseignement de ce double jeu de tests : **les tests décrivent le problème, pas l'implémentation**.

Ce découplage a une conséquence pratique très agréable : les deux implémentations sont **comparables**.
Si la version C++ passe et la version Python échoue sur la même configuration et avec la même tolérance, l'erreur est dans la version Python — et non dans l'énoncé.

*************
Exercices
*************

#. **Prendre la mesure de l'état initial.** Lancez les deux suites (``five_bars_mujoco`` puis ``five_bars_kinematics``). Combien de tests passent dans chacune ? Expliquez l'écart.
#. **Comprendre le décompte.** Retrouvez par le calcul le nombre 64 d'erreurs à partir des listes ``Q_GRID_DEG`` et ``XY_TARGETS`` et des tests qui bouclent dessus.
#. **Observer l'effet de ``subTest``.** Supprimez le ``with self.subTest(...)`` de ``test_matches_mujoco_simulation`` et relancez. Combien d'erreurs obtenez-vous ? Que perdez-vous dans le diagnostic ?
#. **Casser une tolérance.** Dans ``test_home_configuration``, remplacez ``atol=POS_TOL`` par ``rtol=POS_TOL`` (sans ``atol``). Le test est-il plus sévère ou moins sévère ? Pourquoi est-ce dangereux pour un point proche de l'origine ?
#. **Vérifier qu'un test détecte le bug.** Écrivez une implémentation Python de ``forward_kinematics`` qui place la pointe du stylo en ``A3``, comme dans l'exercice 3 de :doc:`p03s02_write_tests_with_gtest`. Les tests Python détectent-ils le même bug, avec les mêmes écarts que la version C++ ?
#. **Ajouter un test de cohérence inter-langages.** Proposez un test qui vérifie que les implémentations C++ et Python donnent le même résultat à 10\ :sup:`-12` près. Où le placeriez-vous, et quelle difficulté pratique faut-il résoudre ?
