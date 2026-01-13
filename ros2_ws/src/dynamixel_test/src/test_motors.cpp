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