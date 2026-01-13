#####################################################
Description du matériel de la plateforme pantographe
#####################################################

Raspberry Pi 5 Specifications (datasheetRPi5_ )
=========================================

- Broadcom BCM2712 2.4GHz quad-core 64-bit Arm Cortex-A76 CPU, with cryptography extensions, 512KB per-core L2 caches and a 2MB shared L3 cache
- VideoCore VII GPU, supporting OpenGL ES 3.1, Vulkan 1.2
- Dual 4Kp60 HDMI® display output with HDR support
- 4Kp60 HEVC decoder
- LPDDR4X-4267 SDRAM (2GB, 4GB, 8GB, and 16GB)
- Dual-band 802.11ac Wi-Fi®
- Bluetooth 5.0 / Bluetooth Low Energy (BLE)
- microSD card slot, with support for high-speed SDR104 mode
- 2 × USB 3.0 ports, supporting simultaneous 5Gbps operation
- 2 × USB 2.0 ports
- Gigabit Ethernet, with PoE+ support (requires separate PoE+ HAT)
- 2 × 4-lane MIPI camera/display transceivers
- PCIe 2.0 x1 interface for fast peripherals (requires separate M.2 HAT or other adapter)
- 5V/5A DC power via USB-C, with Power Delivery support
- Raspberry Pi standard 40-pin header
- Real-time clock (RTC), powered from external battery
- Power button

Raspberry Pi 5 Active Fan Specifications (datasheetRpiF_ )
=========================================

- **Input Voltage:** 5V DC (supplied via 4-pin fan header on Raspberry Pi 5)  
- **Fan Speed Control:** Pulse Width Modulation (PWM) with tachometer  
- **Maximum Airflow:** 1.09 CFM (Cubic Feet per Minute)  
- **Maximum Fan Speed:** 8000 RPM ± 15%  
- **Product Material:** Anodized Aluminum

NVMe Base Specifications (datasheetNVMe_ )
=========================================

Adata Legend 700 Specifications (datasheetAL7_ )
=========================================

- **Capacity:** 256GB
- **Form factor:** M.2 2280
- **NAND Flash:** 3D NAND
- **Dimensions (LxWxH):** 80 x 22 x 3.13mm(with heat sink)
- **Weight:** 9g (with heat sink)
- **Interface:** PCIe Gen3 x4
- **Sequential Read (Max):** Up to 2,000MB/s
- **Sequential Write (Max):** Up to 1,600MB/s
- **Operating temperature:** 0°C - 70°C
- **Storage temperature:** -40°C - 85°C
- **Shock resistance:** 1500G/0.5ms
- **MTBF:** 1,500,000 hours
- **Terabytes Written (TBW):** 480TB
- **Warranty:** 3-year limited warranty

AX-12A Dynamixel (datasheetDYN_ )
=========================================

- **Baud Rate:**	7,843 [bps] ~ 1 [Mbps]
- **Weight:**	AX-12 (53.5 [g]), AX-12+ (53.5 [g]), AX-12A (54.6 [g])
- **Dimensions:** (W x H x D)	32 X 50 X 40 [mm]
- **Resolution:**	0.29 [°]
- **Running Degree:**	0 ~ 300 [°] or Endless Turn
- **Motor:**	Cored
- **Gear Ratio:**	254 : 1
- **Stall Torque:**	1.5 [N.m] (at 12 [V], 1.5 [A])
- **No Load Speed:**	59 [rev/min] (at 12V)
- **Operating Temperature**	-5 ~ +70 [°C]
- **Input Voltage:**	9.0 ~ 12.0 [V] (Recommended : 11.1V)
- **Command Signal:**	Digital Packet
- **Physical Connection:**	TTL Level Multi Drop Bus, Half Duplex Asynchronous Serial Communication, (8bit, 1stop, No Parity)
- **ID:**	254 ID (0~253)
- **Feedback:**	Position, Temperature, Load, Input Voltage, etc
- **Gear Material:**	Engineering Plastic(Full)
- **Case Material:**	Engineering Plastic(Front, Middle, Back)

.. _datasheetRPi5: https://www.raspberrypi.com/products/raspberry-pi-5/

.. _datasheetRPiF: https://www.raspberrypi.com/products/active-cooler/

.. _datasheetNVMe: https://nvmexpress.org/wp-content/uploads/NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf

.. _datasheetAL7: https://www.adata.com/en/consumer/category/ssds/solid-state-drives-legend-700/?tab=description

.. _datasheetDYN: https://emanual.robotis.com/docs/en/dxl/ax/ax-12a/
