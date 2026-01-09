*************************************
Développement informatique avec ROS2
*************************************

| Ce cours est une introduction pratique aux bonnes pratiques de développement informatique en prenant comme cas d'étude le développement de logiciels pour des applications robotiques avec ROS2. ROS2 crée un environnement de développement logiciel générique pour la robotique.
| La robotique étant un très très vaste domaine rassemblant des domaines variés: mécanique, électronique, informatique, intelligence artificielle, contrôle, vision, etc, la quantité de logiciels disponibles à travers ROS2 est très importante. Elle donne la possibilité de développer des applications robotiques complexes en combinant des logiciels existants.
| Pour ce cours cela permet d'étudier un système avancé de développement logiciel permettant d'intégrer des logiciels de différentes natures tout en conservant une cohérence d'ensemble et une qualité de développement la plus grande possible.
| Ce sont des qualités essentielles pour un projet informatique moderne et sont très recherchées dans l'informatique et l'industrie de la robotique.

`ROS2 <https://docs.ros.org/>`_ (Robot Operating System version 2) est conçu pour être utilisé dans des applications industrielles et commerciales, et fournit des outils et des bibliothèques très avancés pour le développement de logiciels pour les robots. Il est basé sur des standards industriels et est conçu pour être utilisé dans des environnements de production.

C'est donc un cas d'étude particulièrement intéressant pour l'apprentissage des bonnes pratiques de développement logiciel.

***************************************
Qu'est-ce qu'un logiciel de qualité ? 
***************************************

| Un logiciel de qualité est un logiciel qui fait ce qu'on lui demande de faire sans erreur ni faille de sécurité, qui est facile à utiliser et qui est facile à maintenir et à faire évoluer.
| Pour ce faire il comporte souvent des bibliothèques permettant un développement modulaire ainsi que la possibilité d'utiliser les fonctionnalités développées pour le logiciel dans d'autres logiciels.
| Pour garantir la fiabilité du logiciel, il est important de concevoir **des tests** dès la conception du logiciel et **d'exécuter les tests** régulièrement pour garantir que le logiciel fonctionne correctement.
| Enfin un logiciel de qualité a un système de **reporting des erreurs et des bugs** qui permet que lorsque des erreurs en production surviennent, celles-ci soient automatiquement loguées et transmises aux développeurs chargés de la maintenance pour qu'ils puissent les corriger rapidement.
| Enfin un logiciel de qualité peut se **mettre à jour automatiquement** pour corriger les erreurs et les bugs et pour ajouter de nouvelles fonctionnalités.


| Pour un industriel, développer un logiciel coûte de l'argent: le salaire des développeurs. Un point très important pour un industriel est de contrôler le coût de développement de son logiciel.
| Pour cela il est important de faciliter au maximum le développement, la maintenance et l'évolution du logiciel.
| Un point essentiel pour cela est la **qualité de la documentation** du logiciel.

En résumé, un logiciel de qualité est un logiciel qui:
   * Fait ce qu'on lui demande de faire sans erreur ni faille de sécurité
   * Est facile à utiliser
   * Est facile à maintenir et à faire évoluer
   * Est bien documenté
   * Est testé régulièrement
   * A un système de reporting des erreurs et des bugs
   * Peut se mettre à jour automatiquement

*****************
Déroulé du cours
*****************

Ce cours vous propose de découvrir l'aventure de la création d'un logiciel pour la robotique depuis sa conception jusqu'à sa mise en production. 
   1. Nous allons nous focaliser d'abord sur la documentation et le système de suivi de version du logiciel.
   2. Ensuite nous allons étudier comment créer un système de tests automatisés pour C++ et Python.
   3. Nous verrons comment utiliser les outils de debugging gdb et valgrind pour identifier, localiser et prévenir les erreurs.
   4. Nous présenterons le reporting d'erreur et les systèmes de mise-à-jour automatiques.

| Tout au long de ce cours nous utiliserons le système ROS2 et des packages particulier de ROS2 pour illustrer les concepts abordés.
| Pour ce cours vous développerez un logiciel de contrôle d'un robot déployé sur un Raspberry Pi.

*****************
Performances
*****************

| Vous avez peut-être noté que nous n'aborderons pas la performance et l'optimisation du code dans ce cours.
| En effet, contrairement à ce que beaucoup de développeurs débutants pensent, la performance au sens de la rapidité d'exécution du code n'est pas un critère de qualité d'un logiciel dans la mesure où le code est suffisamment rapide pour répondre aux besoins de l'utilisateur.
| Cela paraît paradoxal, mais si le logiciel va assez vite pour que sa vitesse d'exécution ne soit pas un problème pour l'utilisateur, alors il n'est pas nécessaire d'optimiser le code.
| Plus important, il ne faut absolument pas optimiser le code avant d'avoir des tests automatisés qui garantissent que le code fonctionne correctement.
| Ceux-ci pourront, en effet, être utilisés par la suite pour vérifier que les optimisations n'ont pas introduit de bugs dans le code.

