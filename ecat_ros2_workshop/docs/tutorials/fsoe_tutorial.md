# FSoE (Fail-Safe over EtherCAT): Safety in Industrial Communication

---

## Introduction to FSoE

**Fail-Safe over EtherCAT (FSoE)** is a safety protocol designed to enable the transmission of **safety-critical data** alongside standard process data on the same EtherCAT network. FSoE leverages the **Black Channel principle**, ensuring that safety is managed at the protocol level rather than the physical medium. This approach allows EtherCAT networks to achieve **SIL 3 (Safety Integrity Level 3)**, making it suitable for applications where human safety is critical, such as robotics, industrial automation, and medical devices.

FSoE is **TÜV-certified** and complies with international standards such as **IEC 61508** and **IEC 61784-3**. It is maintained as an open technology by the **EtherCAT Technology Group (ETG)**.

---

## FSoE Basics and Frame Structure

![FSoE Frame Structure](https://github.com/ICube-Robotics/ecat_ros2_workshop/blob/main/resources/fsoe_frame.png?raw=true)

*Caption: Illustration of the FSoE frame structure, showing how safety data (Safe Data, CMD, CRCs, Connection ID) is embedded within standard EtherCAT frames to ensure integrity and reliability.*

FSoE embeds safety data within standard EtherCAT frames, adding integrity information such as **Cyclic Redundancy Checks (CRC)**, **watchdog timers**, and **connection IDs**. Each FSoE frame includes:

- **Command (CMD)**: Specifies the type of safety command.
- **Safe Data**: Contains safety-related information, such as the status of an emergency stop.
- **CRC_0 and CRC_1**: Used to detect errors in the transmitted data.
- **Connection ID**: Ensures data is sent to and received from the correct devices.

The minimum FSoE frame length is **6 bytes**, but there is no strict upper limit on the size of the safe data. Each 2-byte block of safe data is protected by a 2-byte CRC, ensuring robust error detection.

---

## Network Topologies with FSoE

FSoE supports multiple network topologies, each with unique advantages and use cases.

---

### Centralized Approach

![Centralized FSoE Topology](https://github.com/ICube-Robotics/ecat_ros2_workshop/blob/main/resources/fsoe_arch_centralized.png?raw=true)

*Caption: Diagram of a centralized FSoE topology, where the FSoE Master is integrated into the EtherCAT Master device.*

In a **centralized approach**, the **FSoE Master** is integrated into the **EtherCAT Master device**. This simplifies the system architecture by eliminating the need for SubDevice-to-SubDevice communication. However, the EtherCAT Master device must be **safety-certified**, which can increase costs and complexity.

**Advantages:**
- Simplified configuration.
- Direct control over all safety functions.

**Drawbacks:**
- The EtherCAT Master device must be safety-certified.
- Single point of failure.

**Status in `ethercat_driver_ros2`:**
The centralized approach is **not currently implemented** in the `ethercat_driver_ros2` package.

---

### Decentralized Safety Logic

![Decentralized FSoE Topology](https://github.com/ICube-Robotics/ecat_ros2_workshop/blob/main/resources/fsoe_arch_decentralized.png?raw=true)

*Caption: Diagram of a decentralized FSoE topology, showing the FSoE MainInstance on a separate SubDevice and its communication with other SubInstances.*

In a **decentralized approach**, the **FSoE MainInstance** runs on a **separate EtherCAT SubDevice**. This allows the EtherCAT Master device to remain **non-certified**, simplifying design and reducing costs. Multiple **FSoE SubInstances** (e.g., safe I/O modules, drives) communicate with the FSoE MainInstance via the EtherCAT Master device.

**Advantages:**
- No certification required for the EtherCAT Master device.
- Modularity and fault isolation.

**Use Cases:**
- Safety I/O modules (e.g., emergency stops, safety gates).
- Safe drives and motion control (e.g., STO, SS1, SS2).
- Modular machines with distributed safety devices.

---

## Communication Mechanism in FSoE

FSoE ensures reliable transmission of safety data through **logical safety connections** between the **FSoE MainInstance** and **SubInstances**. Safety frames are exchanged via standard EtherCAT process data, and the EtherCAT Master device must support data copying for SubDevice-to-SubDevice communication.

---

### Copy Infos Configuration File

**[IMAGE PLACEHOLDER: ENI Configuration Example]**
*Caption: Example of an ENI (EtherCAT Network Information) configuration file, showing how data copying is configured for SubDevice-to-SubDevice communication.*

The **ENI (EtherCAT Network Information) file** defines the **source**, **destination**, and **size** of data blocks for SubDevice-to-SubDevice communication. The `ethercat_driver_ros2` software processes these entries to ensure safety data is routed correctly.

---

## Role of MainDevice Software (`ethercat_driver_ros2`)

The **MainDevice**, running `ethercat_driver_ros2`, acts as part of the **Black Channel** and does not need to be safety-certified. It facilitates the transmission of safety data by:

- Reading process-data input.
- Performing data copying based on ENI rules.
- Writing process-data output.

This ensures seamless communication between the **FSoE MainInstance** and **SubInstances**.

---

## Safety Cycle in Decentralized Mode

The **safety cycle** in a decentralized FSoE system involves:

1. The **FSoE MainInstance** sends a safety "MainInstance Frame" to SubInstances.
2. SubInstances reply with their "SubInstance Frames."
3. Safety checks, including **CRC validation**, **connection ID verification**, and **watchdog timers**, are performed.

This cycle ensures reliable transmission of safety data and prompt detection of errors or failures.

---

## Advantages and Use Cases of Decentralized FSoE

The decentralized approach offers several advantages:

- The **EtherCAT Master device** does not need to be safety-certified.
- **Modularity** and **fault isolation** improve system resilience.
- **Use Cases**:
  - Safety I/O modules (e.g., emergency stops, safety gates).
  - Safe drives and motion control (e.g., STO, SS1, SS2).
  - Modular machines with distributed safety devices.

---

## Configuration of FSoE Devices

Configuring FSoE devices involves:

1. **Assigning FSoE Device Addresses**: Using hardware DIP switches or software tools.
2. **Defining Safety Logic**: Using manufacturer tools like **Beckhoff TwinSAFE with TwinCAT**.
3. **Mapping Safety Inputs and Outputs**: Connecting safety signals to logical variables.
4. **Establishing Logical Connections**: Between the FSoE MainInstance and SubInstances.
5. **Configuring SubDevice-to-SubDevice Communication**: Using the ENI file.

---

## Conclusion

FSoE (Fail-Safe over EtherCAT) provides a robust solution for transmitting safety-critical data in industrial applications. Its support for both **centralized** and **decentralized** topologies, combined with the flexibility of the `ethercat_driver_ros2` package, makes it an ideal choice for modern robotics and automation systems. Future developments will focus on enhancing **multi-master redundancy**, **hot-plug support**, and **user-friendly configuration tools**.
