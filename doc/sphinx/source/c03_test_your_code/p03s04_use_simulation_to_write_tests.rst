.. _use_simulation_to_write_tests:

##############################################
Utiliser la simulation pour écrire des tests
##############################################

.. index:: simulation, MuJoCo, oracle de test, vérité terrain

Les deux sections précédentes ont montré **comment** écrire un test, en C++ et en Python.
Il reste la question la plus difficile, et celle qui est propre à la robotique : **qui décide de la valeur attendue ?**

Vérifier que ``2 + 3`` vaut ``5`` ne pose aucun problème. Vérifier qu'un modèle géométrique place la pointe d'un stylo en
:math:`(0{,}0734\ \mathrm{m},\ 0{,}2022\ \mathrm{m})` en est un tout autre : il faut connaître la réponse **avant** d'écrire le code qui la calcule, et sans utiliser ce code.
Le composant qui fournit cette réponse s'appelle un **oracle**, et cette section explique comment une simulation peut en tenir le rôle.

*************************************
Le problème de l'oracle
*************************************

Un test se compose toujours de trois éléments : des entrées, le code à tester, et une **référence** à laquelle comparer le résultat.
C'est le troisième élément qui est difficile à obtenir.

Les stratégies possibles, et leurs limites
===========================================

.. list-table::
   :header-rows: 1
   :widths: 24 38 38

   * - Oracle
     - Principe
     - Limite
   * - **Valeurs calculées à la main**
     - on calcule quelques cas au crayon, ou sur la CAO
     - très peu de points, erreurs de calcul humaines, aucune couverture de l'espace de travail
   * - **Implémentation de référence**
     - on compare à un code déjà validé (autre bibliothèque, code d'un collègue)
     - il faut déjà disposer d'une implémentation en laquelle on a confiance
   * - **Invariants**
     - on vérifie des propriétés vraies pour toute entrée (``IK ∘ FK = id``)
     - deux fonctions **toutes deux fausses** mais réciproques passent le test
   * - **Mesures sur le robot réel**
     - on bouge le robot et on mesure
     - lent, non reproductible, nécessite le matériel et un moyen de mesure externe
   * - **Simulation**
     - un simulateur physique calcule le comportement du mécanisme
     - fidélité limitée au modèle ; il faut valider le simulateur lui-même

Aucune n'est suffisante seule, et les tests du projet 5 barres en combinent quatre : quelques valeurs issues de la CAO, des invariants, des cas d'erreur, et surtout une **simulation** comme référence principale.

Pourquoi le robot réel ne peut pas servir de test unitaire
===========================================================

C'est une tentation naturelle en robotique, et il faut y renoncer pour des raisons pratiques :

#. **Disponibilité** : un seul robot pour un groupe d'étudiants, et aucun robot sur le serveur d'intégration continue.
#. **Vitesse** : une suite de tests doit s'exécuter en quelques secondes pour être lancée à chaque modification. Le projet balaie 16 configurations et 12 cibles, soit une trentaine de mouvements complets — impossible à faire sur un robot à chaque sauvegarde de fichier.
#. **Reproductibilité** : frottements, jeux, dérive thermique des servos et bruit de mesure font qu'une même consigne ne donne jamais deux fois exactement le même résultat. Un test qui n'est pas reproductible est un test instable.
#. **Risque** : un modèle inverse faux envoie des consignes aberrantes. Sur un mécanisme à chaîne fermée comme le 5 barres, cela signifie forcer deux bras l'un contre l'autre — donc casser le matériel.

.. important::

   Les tests sur le robot réel sont **indispensables**, mais ils ne jouent pas le même rôle.
   Ce sont des tests de **validation** (ou de recette) : peu nombreux, lancés rarement, exécutés à la main et sous surveillance.
   Les tests **unitaires**, eux, doivent être nombreux, rapides, reproductibles et automatiques : c'est là que la simulation est irremplaçable.

************************************************************
La simulation comme vérité terrain, et pourquoi c'est valide
************************************************************

L'objection évidente est la suivante : *si je teste mon modèle avec un autre modèle, je ne teste rien.*
Elle serait fondée si les deux calculaient la même chose de la même façon. Toute la validité du dispositif repose sur le fait que ce n'est **pas** le cas.

Deux chemins de calcul indépendants
====================================

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Le code testé
     - La simulation (l'oracle)
   * - Résolution **analytique** : trigonométrie, intersection de deux cercles, formules fermées.
     - Résolution **numérique** : intégration des équations de la dynamique sous contrainte, puis résolution itérative de la fermeture par une méthode de Newton.
   * - Calcule directement la position du stylo à partir de ``q1`` et ``q4``.
     - Asservit deux servos simulés, laisse le mécanisme atteindre son équilibre, puis **lit** la position du repère ``pen_tip``.
   * - Exprime le choix du mode d'assemblage par le signe d'un terme.
     - Reste sur la branche d'assemblage parce que la consigne est appliquée **en rampe** à partir de l'état précédent.
   * - Connaît la géométrie par la structure ``Geometry``.
     - Connaît la géométrie par le fichier MJCF et la contrainte ``<connect>`` en ``A3``.

Les deux n'ont en commun que les **paramètres géométriques** — et ceux-ci sont lus dans un fichier unique, ce qui est précisément ce que l'on veut (voir plus bas).
Une erreur de trigonométrie, de signe, de convention d'angle, de mode d'assemblage ou d'oubli du décalage du stylo n'a aucune raison de se produire à l'identique dans les deux chemins.
C'est ce qui rend la comparaison informative.

.. tip::

   Le principe se généralise bien au-delà de la robotique : un oracle est utile quand il est **indépendant** du code testé, pas quand il est « plus juste ».
   Comparer deux implémentations qui partagent la même formule ne prouve rien ; comparer une formule fermée à une résolution numérique, ou un algorithme optimisé à une version naïve et lente, prouve beaucoup.

La simulation « headless »
===========================

.. index:: headless

La simulation utilisée par les tests tourne **sans affichage** (*headless*) : pas de fenêtre, pas d'OpenGL, pas d'interaction.
Ce n'est pas un détail d'implémentation, c'est une condition pour que les tests soient automatisables :

* ils peuvent tourner sur un serveur d'intégration continue, qui n'a ni écran ni carte graphique (voir :doc:`p03s05_create_CI_for_automatically_runing_your_tests`) ;
* ils tournent **beaucoup** plus vite que le temps réel : un balayage des 16 configurations, soit 16 mouvements complets amenés à l'équilibre, coûte une soixantaine de millisecondes en C++, et la suite entière reste sous la seconde ;
* aucune dépendance graphique n'est nécessaire, ce qui simplifie l'image Docker.

C'est pourquoi le projet sépare soigneusement la simulation (``sim.py``, ``mujoco_five_bars.hpp``) de son affichage (``direct_gui.py``, le *viewer* du ``sim_node``).
Cette séparation est une règle de conception générale : **le calcul ne doit jamais dépendre de son affichage**, sinon il devient intestable.

*********************************
Le banc de test du projet
*********************************

Le harnais C++ : ``mujoco_five_bars.hpp``
==========================================

Côté C++, l'oracle est une classe qui encapsule le modèle MuJoCo et n'expose que ce dont les tests ont besoin.

.. dropdown:: ``test/mujoco_five_bars.hpp`` (fichier complet)

   .. literalinclude:: resources/code/five_bars/kinematics/test/mujoco_five_bars.hpp
      :language: cpp
      :caption: test/mujoco_five_bars.hpp

Trois méthodes font tout le travail, et chacune illustre une précaution à prendre.

**Remettre la simulation dans un état connu.**

.. literalinclude:: resources/code/five_bars/kinematics/test/mujoco_five_bars.hpp
   :language: cpp
   :lines: 68-76

La configuration de référence (``home``) est l'assemblage mesuré sur la CAO. Mais une configuration d'assemblage saisie à la main n'est jamais **exactement** fermée : les 300 pas de simulation laissent la contrainte en ``A3`` se refermer précisément.
C'est une illustration de ce que doit faire une remise à zéro : non pas « recopier des valeurs », mais **rétablir toutes les invariants** de l'état initial.

**Amener le mécanisme à l'équilibre, et savoir si on y est arrivé.**

.. literalinclude:: resources/code/five_bars/kinematics/test/mujoco_five_bars.hpp
   :language: cpp
   :lines: 78-105
   :emphasize-lines: 1-3, 17-27

Trois points essentiels pour la reproductibilité :

#. La consigne est appliquée **en rampe** (``ramp_time``) et non en échelon. Un échelon ferait traverser le mécanisme à grande vitesse et pourrait le faire basculer sur l'**autre mode d'assemblage** : la mesure ne correspondrait plus à la configuration demandée. La rampe suit continûment la branche d'assemblage courante.
#. La fonction attend que les vitesses soient toutes inférieures à un seuil, c'est-à-dire que l'équilibre soit **effectivement** atteint — et pas qu'un temps arbitraire se soit écoulé.
#. Elle **renvoie un booléen** : si l'équilibre n'est pas atteint au bout de 5000 pas, elle le signale au lieu de renvoyer une mesure silencieusement fausse.

**Mesurer la validité de la mesure.**

.. literalinclude:: resources/code/five_bars/kinematics/test/mujoco_five_bars.hpp
   :language: cpp
   :lines: 123-129

La contrainte de fermeture de MuJoCo est résolue numériquement : elle n'est jamais exactement satisfaite.
``closureError()`` donne la distance résiduelle entre les deux points ``A3``, ce qui permet aux tests de **vérifier la qualité de leur propre référence** avant de s'en servir.

Ces deux vérifications sont justement ce que la fixture fait systématiquement, avant de rendre la main au test :

.. literalinclude:: resources/code/five_bars/kinematics/test/test_kinematics.cpp
   :language: cpp
   :lines: 74-81
   :emphasize-lines: 5-6
   :caption: Toute mesure est accompagnée de la vérification de ses conditions de validité

.. important::

   C'est le point le plus transposable de cette section : **un oracle doit pouvoir dire qu'il ne sait pas**.
   Sans les deux vérifications ci-dessus, une simulation qui n'aurait pas convergé fournirait une position parfaitement plausible mais fausse, et le test accuserait le modèle de l'étudiant.
   Un test qui accuse le mauvais coupable est un test nuisible.

Le harnais Python : ``FiveBarsSim``
====================================

Côté Python, la classe ``FiveBarsSim`` du paquet ``five_bars_mujoco`` joue le même rôle, avec la même interface (``reset``, ``settle``, ``pen_position``, ``closure_error``).
Elle est utilisée à la fois par les tests, par les nœuds ROS 2 et par les interfaces graphiques — ce qui est un bon signe : **l'oracle n'est pas du code écrit pour les tests**, c'est le code de production de la simulation.

.. dropdown:: ``five_bars_mujoco/sim.py`` (fichier complet)

   .. literalinclude:: resources/code/five_bars/mujoco/src/sim.py
      :language: python
      :caption: five_bars_mujoco/sim.py

On y retrouve la même logique de convergence :

.. literalinclude:: resources/code/five_bars/mujoco/src/sim.py
   :language: python
   :pyobject: FiveBarsSim.settle

ainsi qu'une résolution **purement cinématique** de la fermeture, par une méthode de Newton utilisant les jacobiennes fournies par MuJoCo :

.. literalinclude:: resources/code/five_bars/mujoco/src/sim.py
   :language: python
   :pyobject: FiveBarsSim.solve_closure

Ce second chemin de calcul est intéressant : la même simulation peut donc fournir sa référence de **deux** façons, dynamique (``settle``) et cinématique (``solve_closure``).
Les faire se confirmer l'une l'autre est l'objet d'un des tests du banc d'essai, comme nous allons le voir.

***************************************
Valider l'oracle avant de s'en servir
***************************************

.. index:: validation du banc de test

Si les tests font confiance à la simulation, alors **la simulation doit elle-même être testée**.
C'est la raison d'être de la suite ``TestFiveBarsSim`` du paquet ``five_bars_mujoco``, qui doit passer dès le départ :

.. literalinclude:: resources/code/five_bars/mujoco/test/test_sim.py
   :language: python
   :caption: ``five_bars_mujoco/test/test_sim.py`` — les tests du banc de test

Regardons ce que chacun apporte, car c'est un modèle de ce qu'il faut vérifier sur un oracle :

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Test
     - Ce qu'il garantit
   * - ``test_home_is_closed``
     - L'état initial est **cohérent** : la chaîne est fermée à 10\ :sup:`-9` m près. Si ce test échoue, le modèle MJCF ou la configuration de référence est en cause, et plus rien d'autre n'est interprétable.
   * - ``test_settle_reaches_command_and_keeps_chain_closed``
     - La simulation **obéit** : les angles mesurés valent les angles demandés à 10\ :sup:`-4` près, et la chaîne reste fermée. C'est l'hypothèse implicite de tous les tests de cinématique.
   * - ``test_command_is_saturated``
     - Les débattements des servos sont respectés : une consigne hors limites est **saturée**, pas appliquée.
   * - ``test_kinematic_closure_matches_dynamic_simulation``
     - Les **deux** méthodes de résolution de la fermeture (dynamique et newtonienne) donnent le même résultat à 10\ :sup:`-5` près. C'est une vérification croisée de l'oracle par lui-même.
   * - ``test_unreachable_configuration_is_reported``
     - Une configuration non assemblable est **signalée** et non silencieusement approximée.

La même précaution est reprise dans la suite de cinématique, sous le nom ``SimulationHarness`` (C++) ou ``TestSimulationHarness`` (Python), avec deux tests qui ancrent la simulation au monde réel :

.. literalinclude:: resources/code/five_bars/kinematics/test/test_kinematics.py
   :language: python
   :pyobject: TestSimulationHarness
   :caption: La simulation est comparée à une mesure faite sur la CAO

Le premier compare la position du stylo à l'alésage du porte-stylo **mesuré sur le modèle CAO** du robot : c'est le seul endroit où une valeur numérique extérieure au logiciel entre dans la chaîne de validation.
Il rattache donc tout l'édifice à la réalité physique du mécanisme, avec une tolérance de 1 mm qui correspond à la précision de la mesure sur la CAO.

.. note::

   Ce sont exactement les tests qui passent dans le projet livré (voir les sorties dans :doc:`p03s02_write_tests_with_gtest` et :doc:`p03s03_write_tests_for_python`).
   Leur rôle est celui d'un **arbitre** : si une suite de cinématique échoue alors que ceux-là passent, l'erreur est dans le modèle de l'étudiant ; s'ils échouent eux aussi, il est inutile de chercher ailleurs que dans l'environnement ou le modèle de simulation.

*****************************************************
Une seule source de vérité pour la géométrie
*****************************************************

Un piège subtil guette ce genre de test : si le code testé et son oracle tiennent chacun leur propre copie des dimensions du robot, les tests échoueront dès que l'une des deux copies changera — et, pire, ils pourront passer alors que le code est faux, parce que les deux copies seront fausses ensemble.

Le projet évite ce piège en désignant un fichier unique comme source de vérité :

.. literalinclude:: resources/code/five_bars/geometry.yaml
   :language: yaml
   :lines: 15-27
   :caption: ``five_bars_description/config/geometry.yaml`` — la seule définition de la géométrie

À partir de ce fichier, un script génère le modèle MuJoCo ; l'URDF le lit par ``xacro`` ; et les tests, eux, **relisent la géométrie dans le modèle MuJoCo** au lieu de la recopier :

.. literalinclude:: resources/code/five_bars/kinematics/test/mujoco_five_bars.hpp
   :language: cpp
   :lines: 131-140
   :caption: La géométrie passée au code testé est extraite du modèle de simulation

.. literalinclude:: resources/code/five_bars/mujoco/src/sim.py
   :language: python
   :pyobject: FiveBarsGeometry.from_model
   :caption: Même extraction, côté Python

La conséquence est très concrète : le modèle testé et la simulation qui le juge parlent **nécessairement** du même robot.
Si vous changez une cote dans ``geometry.yaml`` et régénérez les modèles, les tests continuent de fonctionner sans retouche — ce qui est précisément ce qu'il faut pour un cours où chaque groupe mesure son propre exemplaire du robot.

.. caution::

   Cette technique a une contrepartie qu'il faut connaître : les tests ne vérifient **plus** les valeurs des cotes.
   Une erreur de saisie dans ``geometry.yaml`` donnerait un robot simulé différent du robot réel, et tous les tests passeraient.
   C'est exactement ce que rattrape ``test_home_pen_position_matches_cad``, en comparant à une mesure indépendante faite sur la CAO.
   Toute « source unique de vérité » doit ainsi être confrontée, au moins en un point, à une mesure extérieure.

*****************************************
Choisir les cas de test et les tolérances
*****************************************

Choisir les configurations
===========================

.. literalinclude:: resources/code/five_bars/kinematics/test/test_kinematics.cpp
   :language: cpp
   :lines: 36-58
   :caption: Les configurations et les cibles balayées par les tests

Deux commentaires de deux mots portent ici toute la réflexion.

**« loin des singularités ».** Un mécanisme à chaîne fermée possède des configurations où les bras sont alignés : le mécanisme y perd un degré de liberté, le modèle inverse y devient mal conditionné et la simulation y converge mal.
Tester **au voisinage** d'une singularité ne renseigne ni sur le modèle ni sur la simulation : on y mesure l'instabilité numérique des deux. Les 16 configurations retenues sont donc choisies dans un domaine sain.

**« une zone de dessin »** (``xyTargets``). Les 12 cibles du modèle inverse ne sont pas prises au hasard : ce sont des points du rectangle dans lequel le robot est censé dessiner, c'est-à-dire **le domaine d'usage réel**.
Un test doit couvrir ce que le code fera en production.

.. tip::

   Les singularités et les bords de l'espace de travail ne doivent pas être ignorés pour autant : ils doivent faire l'objet de tests **dédiés**, qui vérifient que le code les **détecte** (en renvoyant ``std::nullopt`` / ``None``) au lieu de produire un résultat douteux.
   C'est le rôle des tests de cas d'erreur du projet.

Choisir les tolérances
=======================

Une simulation introduit ses propres erreurs : pas d'intégration fini, résidu de la contrainte de fermeture, raideur finie de l'asservissement.
Les tolérances doivent donc être choisies **au-dessus** de ces erreurs, et bien en-dessous de l'erreur qu'on veut détecter.

.. list-table::
   :header-rows: 1
   :widths: 18 16 66

   * - Tolérance
     - Valeur
     - Ce qu'elle doit absorber, et rien de plus
   * - ``kPosTol``
     - 0,1 mm
     - Résidu de la contrainte de fermeture et arrondis. Compare deux calculs de la **même** position d'équilibre.
   * - ``kAngleTol``
     - 10\ :sup:`-3` rad
     - Idem, propagé à travers le modèle inverse, où une petite erreur de position se traduit par une erreur d'angle d'autant plus grande que le bras de levier est court.
   * - ``kReachTol``
     - 0,5 mm
     - Ajoute l'**erreur statique de l'asservissement** : les servos simulés sont des actionneurs de position de raideur finie (8 N·m/rad), qui ne rejoignent donc pas exactement leur consigne sous charge.
   * - identité ``IK ∘ FK``
     - 10\ :sup:`-9` rad
     - Aucune simulation n'intervient : deux calculs analytiques enchaînés, seul l'arrondi machine est admissible.

La leçon à retenir est que ces quatre valeurs ne sont pas quatre réglages du même test, mais **quatre exigences différentes**, chacune justifiée par la chaîne de calcul qu'elle juge.
Quand un test échoue de peu, la bonne question n'est jamais « de combien faut-il relâcher la tolérance ? » mais « quelle source d'erreur ai-je oubliée dans mon raisonnement ? ».

*******************************************
Ce que la simulation ne testera jamais
*******************************************

.. index:: sim-to-real gap

Il serait malhonnête de terminer sans dire ce que ce dispositif ne couvre pas. L'écart entre la simulation et la réalité (*sim-to-real gap*) laisse passer :

* les **écarts de fabrication** : les cotes réelles de votre exemplaire diffèrent de la CAO — c'est d'ailleurs pourquoi le projet mesure la CAO plutôt que de recopier le schéma du cours, et pourquoi ``geometry.yaml`` est modifiable ;
* les **jeux, frottements et souplesses** non modélisés des liaisons ;
* le comportement réel des servos : zone morte, résolution finie du codeur, saturation de couple, échauffement ;
* tout ce qui touche à la **communication** avec le matériel : latence du bus Dynamixel, pertes de paquets, erreurs de conversion d'unités entre le pilote et le modèle ;
* les erreurs de **convention partagées** entre le modèle et la simulation : si le MJCF et votre code utilisent tous deux une origine d'angle décalée de la même façon par rapport au robot réel, aucun test ne le verra.

.. warning::

   Des tests unitaires verts ne signifient donc pas que le robot va dessiner correctement.
   Ils signifient quelque chose de plus modeste, mais de très utile : **le modèle géométrique n'est plus un suspect**.
   Quand le robot réel se comportera mal, vous pourrez chercher la cause ailleurs — dans la calibration, le pilote, les unités ou la mécanique — au lieu de douter de tout à la fois.
   C'est exactement ce que l'on attend d'une bonne suite de tests : **réduire l'espace des causes possibles**.

C'est pourquoi la pyramide complète comporte plusieurs étages, dont ce chapitre ne construit que la base :

#. **tests unitaires** sur la simulation headless : nombreux, rapides, automatiques, à chaque ``push`` ;
#. **tests d'intégration** avec ``ros2_control`` et les nœuds, toujours en simulation (le projet fournit ``ros2_control_sim.launch.py`` avec l'option ``use_viewer:=false``) ;
#. **tests de validation** sur le robot réel : rares, manuels, surveillés, et documentés.

*************
Exercices
*************

#. **Faire tourner l'oracle seul.** Lancez les tests de ``five_bars_mujoco``. En quoi diffèrent-ils, par leur objet, des tests de ``five_bars_kinematics`` ?
#. **Casser l'oracle.** Dans ``geometry.yaml``, remplacez ``l2`` par ``0.146300`` (la cote du schéma du cours au lieu de celle de la CAO) et régénérez le modèle avec ``tools/generate_models.py``. Quels tests échouent, et lesquels passent toujours ? Expliquez précisément pourquoi ``test_home_pen_position_matches_cad`` est celui qui détecte le problème.
#. **Supprimer la rampe.** Dans ``settle``, remplacez la rampe par un échelon (``ramp_time`` très petit, ou ``max_speed=None`` côté Python) et observez les configurations extrêmes. Que se passe-t-il, et en quoi cela rendrait-il les tests non reproductibles ?
#. **Ignorer la convergence.** Modifiez la fixture pour ne plus vérifier la valeur de retour de ``settle()`` ni l'erreur de fermeture, puis réduisez fortement le nombre de pas de la boucle d'attente. Les tests échouent-ils franchement, ou de façon trompeuse ? Quelle est la leçon ?
#. **Évaluer l'indépendance de l'oracle.** Serait-il acceptable de tester le modèle direct en comparant son résultat à ``solve_closure()`` de ``FiveBarsSim`` ? Et au modèle inverse du même auteur ? Justifiez dans les deux cas en termes d'indépendance.
#. **Concevoir un test de validation.** Proposez un protocole de test sur le robot réel qui vérifie le modèle géométrique direct. Quel moyen de mesure utiliseriez-vous ? Quelle tolérance viseriez-vous, et pourquoi ne peut-elle pas être de 0,1 mm ?
