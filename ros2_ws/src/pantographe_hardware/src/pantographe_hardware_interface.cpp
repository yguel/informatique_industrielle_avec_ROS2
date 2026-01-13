#include "pantographe_hardware/pantographe_hardware_interface.hpp"

namespace pantographe_hardware{

hardware_interface::CallbackReturn PantographeHardwareInterface::on_init
    (const hardware_interface::HardwareComponentInterfaceParams & params)
{
    if(hardware_interface::SystemInterface::on_init(params) !=
       hardware_interface::CallbackReturn::SUCCESS)
    {
        return hardware_interface::CallbackReturn::ERROR;
    }
 
    info_ = params.hardware_info;

    motor_1_id_ = 1;
    motor_2_id_ = 2;
    port_ = "/dev/ttyUSB0";

    driver_ = std::make_shared<AX12ADriver>(port_);

    return hardware_interface::CallbackReturn::SUCCESS;
}


hardware_interface::CallbackReturn PantographeHardwareInterface::on_configure
    (const rclcpp_lifecycle::State & previous_state)
{
    (void)previous_state;
    if (driver_->init() != 0){
        return hardware_interface::CallbackReturn::ERROR;
    }
    return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn PantographeHardwareInterface::on_activate
    (const rclcpp_lifecycle::State & previous_state)
{
    (void)previous_state;
    set_state("base_motor_1_wheel_joint/velocity", 0.0);
    set_state("base_motor_2_wheel_joint/velocity", 0.0);

    double motor_1_pos = driver_->getPositionRadian(motor_1_id_);
    double motor_2_pos = driver_->getPositionRadian(motor_2_id_);
    set_state("base_motor_1_wheel_joint/position", motor_1_pos);
    set_state("base_motor_2_wheel_joint/position", motor_2_pos);

    driver_->activateWithPositionMode(motor_1_id_);
    driver_->activateWithPositionMode(motor_2_id_);
    return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn PantographeHardwareInterface::on_deactivate
    (const rclcpp_lifecycle::State & previous_state)
{
    (void)previous_state;
    driver_->deactivate(motor_1_id_);
    driver_->deactivate(motor_2_id_);
    return hardware_interface::CallbackReturn::SUCCESS;
}



hardware_interface::return_type PantographeHardwareInterface::read
    (const rclcpp::Time & time, const rclcpp::Duration & period)
{
    (void)time;
    (void)period;
    double motor_1_pos = driver_->getPositionRadian(motor_1_id_);
    double motor_2_pos = driver_->getPositionRadian(motor_2_id_);
    set_state("base_motor_1_wheel_joint/position", motor_1_pos);
    set_state("base_motor_2_wheel_joint/position", motor_2_pos);
    //double motor_1_vel = driver_->getVelocityRadianPerSec(motor_1_id_);
    //double motor_2_vel = driver_->getVelocityRadianPerSec(motor_2_id_);
    //set_state("base_motor_1_wheel_joint/velocity", motor_1_vel);
    //set_state("base_motor_2_wheel_joint/velocity", motor_2_vel);
    return hardware_interface::return_type::OK;
}

hardware_interface::return_type PantographeHardwareInterface::write
    (const rclcpp::Time & time, const rclcpp::Duration & period)
{
    (void)time;
    (void)period;
    driver_->setTargetPositionRadian(motor_1_id_, get_command("base_motor_1_wheel_joint/velocity"));
    driver_->setTargetPositionRadian(motor_2_id_, get_command("base_motor_2_wheel_joint/velocity"));
    return hardware_interface::return_type::OK;
}
} // namespace pantographe_hardware

#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(pantographe_hardware::PantographeHardwareInterface, hardware_interface::SystemInterface)