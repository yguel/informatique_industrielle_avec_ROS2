#ifndef AX12A_DRIVER_HPP
#define AX12A_DRIVER_HPP

// Control table address
#define ADDR_MX_TORQUE_ENABLE           24                  // Control table for AX-12A, may differ in other Dynamixel models
#define ADDR_MX_GOAL_POSITION           30
#define ADDR_MX_GOAL_VELOCITY           32
#define ADDR_MX_PRESENT_POSITION        36
#define ADDR_MX_PRESENT_VELOCITY        38
#define ADDR_CW_ANGLE_LIMIT              6
#define ADDR_CCW_ANGLE_LIMIT             8

#define RAD_TO_DXL_POSITION 195.37860814                    // =1023/(10*pi/6) mapping of [0,300deg] in [0,1023] with input in radians
#define RAD_S_TO_RPM 9.549                                  // 60/(2*pi)
#define RPM_TO_DXL_VELOCITY 4.366812227                     // 1 / 0.229

// Protocol version
#define PROTOCOL_VERSION                1.0                 // See which protocol version is used in the Dynamixel

// Default setting
#define BAUDRATE                        115200
#define DEVICENAME                      "/dev/ttyUSB0"      // Check which port is being used on your controller

#define TORQUE_ENABLE                   1                   // Value for enabling the torque
#define TORQUE_DISABLE                  0                   // Value for disabling the torque
#define CW_ANGLE_LIMIT                  0                   // Dynamixel will rotate between this value
#define CCW_ANGLE_LIMIT                 1023                // and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
#define DXL_MOVING_STATUS_THRESHOLD     10                  // Dynamixel moving status threshold


#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <cstring>
#include <iostream>             
#include <dynamixel_sdk/dynamixel_sdk.h>                    // Uses Dynamixel SDK library
             

class AX12ADriver {
    public:
        AX12ADriver(std::string device_name){
            portHandler_ = dynamixel::PortHandler::getPortHandler(device_name.c_str());
            packetHandler_ = dynamixel::PacketHandler::getPacketHandler(PROTOCOL_VERSION);
        }
    
        int init() {
            std::cout << "Initializing connection with Motors." << std::endl;
    
            // Open port
            if (portHandler_->openPort()) {
                std::cout << "Succeeded to open the port!" << std::endl;
            }
            else {
                std::cout << "Failed to open the port!" << std::endl;
                return -1;
            }
    
            // Set port baudrate
            if (portHandler_->setBaudRate(BAUDRATE)) {
                std::cout << "Succeeded to change the baudrate!" << std::endl;
            }
            else {
                std::cout << "Failed to change the baudrate!" << std::endl;
                return -1;
            } 
            return 0;
        }
    
        void activateWithPositionMode(int dxl_id)
        {
            std::cout << "Activate motor" << std::endl;
    
            // Set Position Control Mode, done by setting both CW and CCW angle limits
            packetHandler_->write2ByteTxRx(portHandler_, dxl_id, ADDR_CW_ANGLE_LIMIT, CW_ANGLE_LIMIT);
            packetHandler_->write2ByteTxRx(portHandler_, dxl_id, ADDR_CCW_ANGLE_LIMIT, CCW_ANGLE_LIMIT);
            
            // Enable Torque
            packetHandler_->write1ByteTxRx(portHandler_, dxl_id, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE);
        }
    
        void deactivate(int dxl_id)
        {
            std::cout << "Deactivate motor" << std::endl;
    
            // Disable Torque
            packetHandler_->write1ByteTxRx(portHandler_, dxl_id, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE);
        }
    
        void setTargetPositionRadian(int dxl_id, double command) 
        {
            int dxl_cmd = command * RAD_TO_DXL_POSITION;
            packetHandler_->write2ByteTxRx(portHandler_, dxl_id, ADDR_MX_GOAL_POSITION, dxl_cmd);
        }
    
        double getPositionRadian(int dxl_id) 
        {
            int16_t dxl_present_position = 0;
            packetHandler_->read2ByteTxRx(portHandler_, dxl_id, ADDR_MX_PRESENT_POSITION, (uint16_t*)&dxl_present_position);
            return (double)dxl_present_position / RAD_TO_DXL_POSITION;
        }
    
    private:
        dynamixel::PortHandler *portHandler_;
        dynamixel::PacketHandler *packetHandler_;
};

#endif