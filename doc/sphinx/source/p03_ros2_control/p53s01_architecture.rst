#########################
Architecture ros2_control
#########################

**Vue rapide du système**

- Les contrôleurs ROS 2 envoient des commandes.
- **ros2_control** orchestre les ressources et transmet les ordres au matériel.
- ``PantographeHardwareInterface`` traduit les commandes vers les moteurs et remonte les états.
- ``AX12ADriver`` gère le protocole Dynamixel.
- Les servomoteurs **Dynamixel AX-12A** (q1, q4) exécutent les mouvements.

.. code-block:: text

   ┌─────────────────────────────────────────┐
   │    Contrôleurs ROS 2                    │
   │  (position_controller, etc.)            │
   └──────────────┬──────────────────────────┘
                  │ commandes
   ┌──────────────▼──────────────────────────┐
   │    ros2_control Framework               │
   │  (resource_manager, controller_manager) │
   └──────────────┬──────────────────────────┘
                  │ état/commandes
   ┌──────────────▼──────────────────────────┐
   │  PantographeHardwareInterface           │
   │  (read, write, lifecycle)               │
   └──────────────┬──────────────────────────┘
                  │ API driver
   ┌──────────────▼──────────────────────────┐
   │          AX12ADriver                    │
   │  (communication Dynamixel SDK)          │
   └──────────────┬──────────────────────────┘
                  │ bus TTL
   ┌──────────────▼──────────────────────────┐
   │   Servomoteurs Dynamixel AX-12A         │
   │   (moteurs q1 et q4)                    │
   └─────────────────────────────────────────┘

**Points clés**

- Cycle de vie : l'interface matérielle suit le Lifecycle ROS 2 pour des transitions sûres.
- Commandes : position angulaire en radians.
- État : positions angulaire en radians remontées; lecture de vitesse non implémentée.
