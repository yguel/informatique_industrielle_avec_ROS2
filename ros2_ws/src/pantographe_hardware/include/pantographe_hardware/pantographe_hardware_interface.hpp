#ifndef PANTOGRAPHE_HARDWARE_INTERFACE_HPP
#define PANTOGRAPHE_HARDWARE_INTERFACE_HPP

#include "hardware_interface/system_interface.hpp"
#include "pantographe_hardware/ax12a_driver.hpp"

namespace pantographe_hardware {

class PantographeHardwareInterface : public hardware_interface::SystemInterface 
{
public:
    // Lifecycle node override
    hardware_interface::CallbackReturn
        on_configure(const rclcpp_lifecycle::State & previous_state) override;
    hardware_interface::CallbackReturn
        on_activate(const rclcpp_lifecycle::State & previous_state) override;
    hardware_interface::CallbackReturn
        on_deactivate(const rclcpp_lifecycle::State & previous_state) override;

    // SystemInterface override
    hardware_interface::CallbackReturn
        on_init(const hardware_interface::HardwareComponentInterfaceParams & params) override;
    hardware_interface::return_type
        read(const rclcpp::Time & time, const rclcpp::Duration & period) override;
    hardware_interface::return_type
        write(const rclcpp::Time & time, const rclcpp::Duration & period) override;      

private:
    std::shared_ptr<AX12ADriver> driver_;
    int motor_1_id_;
    int motor_2_id_;
    std::string port_;

}; // class PantographeHardwareInterface

} // namespace pantographe_hardware


#endif