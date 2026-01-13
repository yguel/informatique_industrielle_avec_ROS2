##########################
Driver Dynamixel AX-12A
##########################

Nous avons développé un driver pour interfacer les servomoteurs Dynamixel AX-12A avec ROS 2. Pour ce faire, nous nous sommes basés sur l'exemple read_write fourni dans le `Dynamixel SDK <https://github.com/ROBOTIS-GIT/DynamixelSDK/blob/main/c%2B%2B/example/protocol1.0/read_write/read_write.cpp>`_.

Le code source de ce driver est disponible dans le package **pantographe_hardware** sous ``include/pantographe_hardware/ax12a_driver.hpp``.

.. note::

   Ce driver est une implémentation basique qui ne supporte que le contrôle et la lecture de position des servomoteurs en mode joint (position control mode).

*********************
Architecture du driver
*********************

Le driver ``AX12ADriver`` est une classe C++ qui encapsule des fonctionnalités du Dynamixel SDK pour simplifier l'utilisation des servomoteurs AX-12A.

Paramètres de configuration
============================

Les paramètres suivants sont définis dans le fichier d'en-tête :

- **Protocole** : Version 1.0 
- **Baudrate** : 115200 bps
- **Port série** : ``/dev/ttyUSB0`` 

Table de contrôle 
=================

Le driver exploite les registres documentés dans le manuel des AX-12A dans la `table de contrôle <https://emanual.robotis.com/docs/en/dxl/ax/ax-12a/#control-table-of-eeprom-area>`_.

Conversions d'unités
====================

Il convient de convertir les unités entre les radians utilisés dans ROS 2 et celles attendues par les servomoteurs Dynamixel AX-12A.

- **RAD_TO_DXL_POSITION** : ``195.37860814`` (conversion radians → position Dynamixel)
  
  - Plage : ``[0, 300°]`` → ``[0, 1023]``
  - Formule : ``1023 / (10π/6)``

.. note:: 

   Bien que le driver ne support actuellement que le mode position, une méthode de conversion pour la lecture de vitesse peut être ajoutée aisément ultérieurement. 

*********************
Méthodes principales
*********************

Initialisation
==============

.. code-block:: cpp

   AX12ADriver driver("/dev/ttyUSB0");
   int result = driver.init();

La méthode ``init()`` :

1. Ouvre le port série spécifié
2. Configure le baudrate à 115200 bps
3. Retourne ``0`` en cas de succès, ``-1`` en cas d'erreur

Activation du moteur
====================

.. code-block:: cpp

   driver.activateWithPositionMode(dxl_id);

Cette méthode :

1. Configure le moteur en mode position (joint mode) en définissant les limites d'angle CW à 0 et CCW à 1023
2. Active le moteur (torque enable)

Désactivation du moteur
========================

.. code-block:: cpp

   driver.deactivate(dxl_id);

Désactive le moteur.

Contrôle de position
====================

.. code-block:: cpp

   // Définir une position cible en radians
   driver.setTargetPositionRadian(dxl_id, 1.57); // π/2 rad = 90°

Envoie une consigne de position au moteur. La conversion radians → unités Dynamixel est effectuée automatiquement.

Lecture de position
===================

.. code-block:: cpp

   // Lire la position actuelle en radians
   double position = driver.getPositionRadian(dxl_id);

Lit la position actuelle du moteur et la retourne en radians.

*********************
Exemple d'utilisation
*********************

.. note::

   Cet exemple est issu du package **dynamixel_test** inclus dans le dépôt GitHub du projet. Il peut être compilé et exécuté pour tester le driver et les moteurs grace à la commande suivante:

.. code-block:: bash

      cd ~/pantographe_dessin_robotise/ros2_ws
      colcon build --packages-select dynamixel_test
      ros2 run dynamixel_test test_motors.cpp

.. code-block:: cpp

   #include "rclcpp/rclcpp.hpp"
   #include "dynamixel_test/ax12a_driver.hpp"
   #include <thread>

   using namespace std::chrono_literals;

   int main()
   {
      int dxl_id_1 = 1;
      int dxl_id_2 = 2;

      auto driver = AX12ADriver("/dev/ttyUSB0");
      driver.init();
      std::this_thread::sleep_for(1s);

      // Test motor position mode 
      driver.activateWithPositionMode(dxl_id_1);
      driver.activateWithPositionMode(dxl_id_2);
      driver.setTargetPositionRadian(dxl_id_1, 2.6);
      driver.setTargetPositionRadian(dxl_id_2, 2.6);

      std::this_thread::sleep_for(5s);

      double pos1 = driver.getPositionRadian(dxl_id_1);
      double pos2 = driver.getPositionRadian(dxl_id_2);
      std::cout << "Motor 1 position (rad): " << pos1 << std::endl;
      std::cout << "Motor 2 position (rad): " << pos2 << std::endl;
      driver.deactivate(dxl_id_1);
      driver.deactivate(dxl_id_2);
   
      return 0;
   }

.. note::

   Cet exemple initialise deux servomoteurs AX-12A, les configure en mode position, leur envoie une consigne de position de 2.6 radians soit le milieu de la plage de rotation, attend 5 secondes, lit et affiche leurs positions actuelles, puis désactive les moteurs.

*********************
Limitations actuelles
*********************

.. warning::

   Le driver présente les limitations suivantes :

   - **Pas de contrôle de vitesse** : Seul le mode position est implémenté
   - **Pas de lecture de vitesse** : La vitesse actuelle n'est pas accessible
   - **Configuration matérielle figée** : Le baudrate et les limites d'angle sont définis en dur

*********************
Améliorations futures
*********************

Les améliorations suivantes sont envisagées :

1. Lecture de la vitesse actuelle
2. Configuration dynamique des paramètres (baudrate, limites)
3. Contrôle de profil de vitesse pour des mouvements plus fluides
4. Ajout du mode roue (wheel mode) pour rotation continue