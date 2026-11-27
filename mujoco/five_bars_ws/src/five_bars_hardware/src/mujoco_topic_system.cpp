// Copyright 2026
// Licence Apache-2.0

#include "five_bars_hardware/mujoco_topic_system.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <string>
#include <unordered_map>
#include <vector>

#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "pluginlib/class_list_macros.hpp"

namespace five_bars_hardware
{

using hardware_interface::CallbackReturn;
using hardware_interface::HW_IF_EFFORT;
using hardware_interface::HW_IF_POSITION;
using hardware_interface::HW_IF_VELOCITY;
using hardware_interface::return_type;

namespace
{
std::string param_or(
  const std::unordered_map<std::string, std::string> & params, const std::string & key,
  const std::string & default_value)
{
  const auto it = params.find(key);
  return it == params.end() ? default_value : it->second;
}

bool to_bool(const std::string & s)
{
  std::string l = s;
  std::transform(l.begin(), l.end(), l.begin(), ::tolower);
  return l == "true" || l == "1" || l == "yes";
}
}  // namespace

CallbackReturn MujocoTopicSystem::on_init(
  const hardware_interface::HardwareComponentInterfaceParams & params)
{
  if (hardware_interface::SystemInterface::on_init(params) != CallbackReturn::SUCCESS) {
    return CallbackReturn::ERROR;
  }
  const auto & info = get_hardware_info();
  const auto & hw = info.hardware_parameters;
  command_topic_ = param_or(hw, "command_topic", command_topic_);
  state_topic_ = param_or(hw, "state_topic", state_topic_);
  state_timeout_ = std::stod(param_or(hw, "state_timeout", "10.0"));
  publish_only_on_change_ = to_bool(param_or(hw, "publish_only_on_change", "true"));

  if (info.joints.size() != 2) {
    RCLCPP_ERROR(
      get_logger(), "Le système 5 barres attend exactement 2 joints actionnés (q1, q4), %zu déclarés.",
      info.joints.size());
    return CallbackReturn::ERROR;
  }
  for (const auto & joint : info.joints) {
    if (joint.command_interfaces.size() != 1 ||
      joint.command_interfaces[0].name != HW_IF_POSITION)
    {
      RCLCPP_ERROR(
        get_logger(), "Joint '%s' : une seule command interface '%s' est supportée.",
        joint.name.c_str(), HW_IF_POSITION);
      return CallbackReturn::ERROR;
    }
    bool has_pos = false, has_vel = false, has_eff = false;
    for (const auto & si : joint.state_interfaces) {
      has_pos |= si.name == HW_IF_POSITION;
      has_vel |= si.name == HW_IF_VELOCITY;
      has_eff |= si.name == HW_IF_EFFORT;
    }
    if (!has_pos) {
      RCLCPP_ERROR(
        get_logger(), "Joint '%s' : state interface '%s' obligatoire.", joint.name.c_str(),
        HW_IF_POSITION);
      return CallbackReturn::ERROR;
    }
    joint_names_.push_back(joint.name);
    has_velocity_.push_back(has_vel);
    has_effort_.push_back(has_eff);
  }
  last_published_.assign(joint_names_.size(), std::numeric_limits<double>::quiet_NaN());
  return CallbackReturn::SUCCESS;
}

CallbackReturn MujocoTopicSystem::on_configure(const rclcpp_lifecycle::State &)
{
  // Le nœud fourni par le framework est déjà ajouté à l'exécuteur du controller_manager.
  auto node = get_node();
  command_pub_ = node->create_publisher<CommandMsg>(command_topic_, rclcpp::SystemDefaultsQoS());
  state_sub_ = node->create_subscription<JointStateMsg>(
    state_topic_, rclcpp::SensorDataQoS().keep_last(1).reliable(),
    [this](const JointStateMsg::SharedPtr msg) {on_state(msg);});
  RCLCPP_INFO(
    get_logger(), "Commandes -> '%s' ; états <- '%s'", command_topic_.c_str(),
    state_topic_.c_str());
  return CallbackReturn::SUCCESS;
}

void MujocoTopicSystem::on_state(const JointStateMsg::SharedPtr msg)
{
  // Callback hors temps réel : on ne fait que déposer le pointeur dans le buffer.
  state_buffer_.writeFromNonRT(msg);
}

CallbackReturn MujocoTopicSystem::on_activate(const rclcpp_lifecycle::State &)
{
  activation_time_ = get_clock()->now();
  timeout_reported_ = false;
  // Aucune consigne n'est envoyée tant que les contrôleurs n'en ont pas écrit une
  // (commande NaN) : le simulateur garde sa position courante à l'activation.
  for (const auto & name : joint_names_) {
    set_command(name + "/" + HW_IF_POSITION, std::numeric_limits<double>::quiet_NaN());
  }
  std::fill(
    last_published_.begin(), last_published_.end(), std::numeric_limits<double>::quiet_NaN());
  return CallbackReturn::SUCCESS;
}

CallbackReturn MujocoTopicSystem::on_deactivate(const rclcpp_lifecycle::State &)
{
  return CallbackReturn::SUCCESS;
}

CallbackReturn MujocoTopicSystem::on_cleanup(const rclcpp_lifecycle::State &)
{
  command_pub_.reset();
  state_sub_.reset();
  return CallbackReturn::SUCCESS;
}

return_type MujocoTopicSystem::read(const rclcpp::Time & time, const rclcpp::Duration &)
{
  const auto msg_ptr = state_buffer_.readFromRT();
  if (!msg_ptr || !(*msg_ptr)) {
    if (!timeout_reported_ && (time - activation_time_).seconds() > state_timeout_) {
      RCLCPP_WARN(
        get_logger(),
        "Aucun état reçu sur '%s' depuis %.1f s : le simulateur five_bars_mujoco/sim_node "
        "est-il lancé ?", state_topic_.c_str(), state_timeout_);
      timeout_reported_ = true;
    }
    return return_type::OK;
  }
  const auto & msg = **msg_ptr;
  for (size_t i = 0; i < joint_names_.size(); ++i) {
    const auto it = std::find(msg.name.begin(), msg.name.end(), joint_names_[i]);
    if (it == msg.name.end()) {
      continue;
    }
    const auto k = static_cast<size_t>(std::distance(msg.name.begin(), it));
    if (k < msg.position.size()) {
      set_state(joint_names_[i] + "/" + HW_IF_POSITION, msg.position[k]);
    }
    if (has_velocity_[i] && k < msg.velocity.size()) {
      set_state(joint_names_[i] + "/" + HW_IF_VELOCITY, msg.velocity[k]);
    }
    if (has_effort_[i] && k < msg.effort.size()) {
      set_state(joint_names_[i] + "/" + HW_IF_EFFORT, msg.effort[k]);
    }
  }
  if (!state_received_) {
    state_received_ = true;
    RCLCPP_INFO(get_logger(), "Premier état reçu du simulateur MuJoCo.");
  }
  return return_type::OK;
}

return_type MujocoTopicSystem::write(const rclcpp::Time &, const rclcpp::Duration &)
{
  std::vector<double> cmd(joint_names_.size());
  bool changed = false;
  for (size_t i = 0; i < joint_names_.size(); ++i) {
    cmd[i] = get_command<double>(joint_names_[i] + "/" + HW_IF_POSITION);
    if (!std::isfinite(cmd[i])) {
      return return_type::OK;  // pas encore de consigne d'un contrôleur
    }
    changed |= !(std::abs(cmd[i] - last_published_[i]) < 1e-9);  // vrai aussi si NaN
  }
  if (publish_only_on_change_ && !changed) {
    return return_type::OK;
  }
  CommandMsg msg;
  msg.data = cmd;
  command_pub_->publish(msg);
  last_published_ = cmd;
  return return_type::OK;
}

}  // namespace five_bars_hardware

PLUGINLIB_EXPORT_CLASS(five_bars_hardware::MujocoTopicSystem, hardware_interface::SystemInterface)
