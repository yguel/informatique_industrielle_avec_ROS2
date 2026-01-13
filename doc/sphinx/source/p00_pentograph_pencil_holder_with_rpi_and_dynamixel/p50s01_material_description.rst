=====================================================
Description du Matériel de notre maquette Pantographe
=====================================================

Dans cette partie nous alons décrire les éléments de la platforme pantographe. Comme vu dans la partie précédente, notre maquette est constitué d'une **Raspberry Pi 5** pour le calcul, un stockage **NVMe haute vitesse** pour la réactivité du système, et des servomoteurs **Dynamixel** pour la partie mécanique.

-----------------------------------------------------

1. Unité de Contrôle et Gestion Thermique
=========================================

Raspberry Pi 5 (`Raspberry Pi 5 datasheet <https://www.raspberrypi.com/products/raspberry-pi-5/>`_)
--------------
C'est l'élément central qui va assurer le traitement des données et le contrôle des moteurs.


- Broadcom BCM2712 2.4GHz quad-core 64-bit Arm Cortex-A76 CPU, with cryptography extensions, 512KB per-core L2 caches and a 2MB shared L3 cache
- VideoCore VII GPU, supporting OpenGL ES 3.1, Vulkan 1.3
- 4Kp60 HEVC decoder
- Dual 4Kp60 HDMI® display output with HDR support
- LPDDR4X-4267 SDRAM (1GB, 2GB, 4GB, 8GB, and 16GB)
- Dual-band 802.11ac Wi-Fi®
- 2 × USB 3.0 ports, supporting simultaneous 5Gbps operation
- 2 × USB 2.0 ports
- 5V/5A DC power via USB-C, with Power Delivery support
- Bluetooth 5.0 / Bluetooth Low Energy (BLE)
- microSD card slot, with support for high-speed SDR104 mode
- Gigabit Ethernet, with PoE+ support (requires separate PoE+ HAT)
- 2 × 4-lane MIPI camera/display transceivers
- PCIe 2.0 x1 interface for fast peripherals (requires separate M.2 HAT or other adapter)
- Raspberry Pi standard 40-pin header
- Real-time clock (RTC), powered from external battery
-Power button


Refroidissement à l'aide d'un ventilateur (`Raspberry Pi Active Cooler <https://www.raspberrypi.com/products/active-cooler/>`_)
-------------------------------------
Ensuite, l'utilisaiton d'un ventilateur pour garantir un maintien des performances du processeur :

* **Type** : Dissipateur thermique en aluminium anodisé avec ventilateur intégré.
* **Tension d'entrée** : 5V DC fourni via le connecteur ventilateur à 4 broches du Raspberry Pi 5.
* **Contrôle de vitesse** : Modulation de largeur d'impulsion (PWM) avec retour tachymétrique.
* **Débit d'air maximum** : 1.09 CFM (pieds cubes par minute).
* **Vitesse maximale** : 8000 RPM ± 15% (tours par minute).
* **Matériau** : Aluminium anodisé.

-----------------------------------------------------

2. Solution de Stockage Haute Performance
=========================================

En intégrant un SSD NVMe dans notre maquette, cela permet d'avoir de meilleures performances de stockage en temps réel. Cela améliore donc la réactivité et la fiabilité tout en réduisant les temps de latence.


SSD Adata Legend 700 (`Adata Legend 700 datasheet <https://www.adata.com/en/consumer/category/ssds/solid-state-drives-legend-700/>`_)
--------------------
* **Capacité** : 512 GB / 1 TB
* **Format** : M.2 2280
* **Interface** : PCIe Gen3 x4
* **Mémoire Flash** : 3D NAND
* **Dimensions (L x l x H)** : 
    - Avec dissipateur : 80 x 22 x 3.13 mm
    - Sans dissipateur : 80 x 22 x 2.15 mm
* **Poids** : 
    - Avec dissipateur : 9 g
    - Sans dissipateur : 6.2 g
* **Performances** :
    - Lecture séquentielle (Max) : Jusqu'à 2000 MB/s
    - Écriture séquentielle (Max) : Jusqu'à 1600 MB/s
* **Fiabilité et Durabilité** :
    - MTBF : 1 500 000 heures
    - TBW (Total Bytes Written) : 320 TB
    - Résistance aux chocs : 1500G / 0.5 ms
* **Températures** :
    - Fonctionnement : 0°C à 70°C
    - Stockage : -40°C à 85°C

-----------------------------------------------------

3. Actionneurs 
===========================

Dynamixel AX-12A (`AX-12A Dynamixel datasheet <https://emanual.robotis.com/docs/en/dxl/ax/ax-12a/>`_)
--------------
Le pantographe est articulé par des servomoteurs Dynamixel AX-12A permettant un retour d'information précis. 

* **Performances** :
    - **Couple à l'arrêt** : 1.5 N.m (à 12V, 1.5A)
    - **Vitesse à vide** : 59 tr/min (à 12V)
    - **Résolution** : 0.29°
    - **Angle de rotation** : 0° à 300° (ou mode rotation continue)

* **Électronique et Alimentation** :
    - **Tension d'entrée** : 9.0V à 12.0V (Recommandé : 11.1V)
    - **Moteur** : Moteur à noyau (Cored)
    - **Rapport de réduction** : 254:1

* **Communication et Contrôle** :
    - **Signal** : Paquet numérique (Digital Packet)
    - **Protocole** : Bus TTL Multi-drop, série asynchrone half-duplex (8-bit, 1-stop, sans parité)
    - **Vitesse (Baud Rate)** : 7,843 bps à 1 Mbps
    - **ID** : 254 adresses uniques (0 à 253)
    - **Retour d'information** : Position, température, charge, tension d'entrée, etc.

* **Physique** :
    - **Dimensions** : 32 x 50 x 40 mm
    - **Poids** : 54.6 g
    - **Matériau** : Engrenages et boîtier en plastique technique haute résistance
    - **Température de fonctionnement** : -5°C à +70°C

