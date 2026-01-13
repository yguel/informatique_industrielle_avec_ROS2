###################################
Interface matérielle (Hardware Interface)
###################################

.. warning::
   **Ce code n'a pas encore été testé ni validé.**
   Il est a traiter en tant que tel et à manipuler avec la plus grande des précautions par des utilisateurs expérimentés uniquement.

L'interface matérielle ``PantographeHardwareInterface`` est le pont entre **ros2_control** et les servomoteurs Dynamixel AX-12A. Elle hérite de ``hardware_interface::SystemInterface``.

Code source : ``include/pantographe_hardware/pantographe_hardware_interface.hpp`` ``src/pantographe_hardware_interface.cpp``

***********************
Cycle de vie (Lifecycle)
***********************

L'interface utilise le modèle **Lifecycle Node** de ROS 2 pour une gestion sécurisée du matériel :

.. code-block:: text

   Unconfigured → Configure → Inactive → Activate → Active
                                ↑           ↓
                                └─ Deactivate

Voir la `documentation ROS 2 Lifecycle <https://design.ros2.org/articles/node_lifecycle.html>`_.

Méthodes principales
=====================

**on_init()** 
   Initialise le driver et les paramètres (IDs des moteurs, port série)

**on_configure()** 
   Ouvre la connexion série avec le convertisseur U2D2 (baudrate : 115200 bps)

**on_activate()** 
   Lit les positions initiales des moteurs et active le couple en mode position

**on_deactivate()** 
   Désactive le couple des moteurs (permet manipulation manuelle)

**read()** 
   Lit les positions actuelles des moteurs et met à jour les état_interfaces

**write()** 
   Envoie les consignes de position aux moteurs
