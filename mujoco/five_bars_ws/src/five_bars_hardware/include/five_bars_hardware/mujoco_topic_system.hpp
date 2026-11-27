// Copyright 2026
// Licence Apache-2.0
//
// Hardware interface ros2_control du système 5 barres simulé dans MuJoCo.
//
// Le simulateur (five_bars_mujoco/sim_node) tourne dans son propre processus ;
// ce composant dialogue avec lui uniquement par topics :
//
//   write() : publie la consigne [q1, q4] (std_msgs/Float64MultiArray)
//             sur `command_topic`  — le MÊME topic que l'IHM à curseurs ;
//   read()  : recopie la dernière mesure reçue sur `state_topic`
//             (sensor_msgs/JointState : joint_q1, joint_q4) dans les state interfaces.
//
// Paramètres <hardware> (URDF, balise <ros2_control>) :
//   command_topic          (défaut /five_bars/joint_commands)
//   state_topic            (défaut /five_bars/sim/actuated_joint_states)
//   state_timeout          (s, défaut 10) : avertit si aucun état n'est reçu
//   publish_only_on_change (bool, défaut true) : ne publie que si la consigne change,
//                          ce qui permet à l'IHM et à ros2_control de partager le topic.
//
// Remplacer ce composant par un hardware interface Dynamixel suffit pour passer
// au robot réel : contrôleurs, URDF (hors balise <hardware>) et state updater restent identiques.

#ifndef FIVE_BARS_HARDWARE__MUJOCO_TOPIC_SYSTEM_HPP_
#define FIVE_BARS_HARDWARE__MUJOCO_TOPIC_SYSTEM_HPP_

#include <memory>
#include <string>
#include <vector>

#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/types/hardware_component_interface_params.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/state.hpp"
#include "realtime_tools/realtime_buffer.hpp"
#include "sensor_msgs/msg/joint_state.hpp"
#include "std_msgs/msg/float64_multi_array.hpp"

namespace five_bars_hardware
{

class MujocoTopicSystem : public hardware_interface::SystemInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(MujocoTopicSystem)

  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareComponentInterfaceParams & params) override;

  hardware_interface::CallbackReturn on_configure(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_activate(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_deactivate(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_cleanup(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::return_type read(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

  hardware_interface::return_type write(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  using JointStateMsg = sensor_msgs::msg::JointState;
  using CommandMsg = std_msgs::msg::Float64MultiArray;

  void on_state(const JointStateMsg::SharedPtr msg);

  // Paramètres
  std::string command_topic_{"/five_bars/joint_commands"};
  std::string state_topic_{"/five_bars/sim/actuated_joint_states"};
  double state_timeout_{10.0};
  bool publish_only_on_change_{true};

  // Joints déclarés dans l'URDF, dans l'ordre (attendu : joint_q1, joint_q4)
  std::vector<std::string> joint_names_;
  std::vector<bool> has_velocity_, has_effort_;

  // Communication avec le simulateur
  rclcpp::Publisher<CommandMsg>::SharedPtr command_pub_;
  rclcpp::Subscription<JointStateMsg>::SharedPtr state_sub_;
  realtime_tools::RealtimeBuffer<JointStateMsg::SharedPtr> state_buffer_;

  std::vector<double> last_published_;
  bool state_received_{false};
  rclcpp::Time activation_time_;
  bool timeout_reported_{false};
};

}  // namespace five_bars_hardware

#endif  // FIVE_BARS_HARDWARE__MUJOCO_TOPIC_SYSTEM_HPP_
