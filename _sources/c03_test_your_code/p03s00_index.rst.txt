###############
Tester le code
###############

Un code qui n'est pas testé est un code dont personne ne sait ce qu'il fait — y compris son auteur, dès qu'il y revient quelques semaines plus tard.
Ce chapitre présente comment écrire des tests, comment les faire exécuter par ROS 2, et comment les faire exécuter automatiquement à chaque modification publiée.

Les quatre dernières sections s'appuient sur un **projet support commun** : la simulation MuJoCo du système 5 barres du cours (voir :ref:`mechanical_description`), dans laquelle les modèles géométriques direct et inverse sont à écrire, en C++ et en Python, et dont les tests sont fournis.
La démarche suivie est celle du développement piloté par les tests : **les tests existent avant le code, et échouent**.

.. toctree::
   :maxdepth: 2

   p03s01_run_ros2_tests
   p03s02_write_tests_with_gtest
   p03s03_write_tests_for_python
   p03s04_use_simulation_to_write_tests
   p03s05_create_CI_for_automatically_runing_your_tests
   p03s06_cheatsheet_five_bars
