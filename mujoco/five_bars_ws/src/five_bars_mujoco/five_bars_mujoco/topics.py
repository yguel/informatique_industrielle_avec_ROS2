"""Noms des topics partagés par le simulateur, l'IHM, ros2_control et le state updater.

    IHM curseurs ──┐
                   ├──> COMMAND_TOPIC (std_msgs/Float64MultiArray, data = [q1, q4] en rad)
    ros2_control ──┘          │   (hardware interface five_bars_hardware/MujocoTopicSystem, write())
                              v
                     five_bars_sim_node (MuJoCo)
                              │
                              ├──> SIM_ACTUATED_STATE_TOPIC (sensor_msgs/JointState : joint_q1, joint_q4)
                              │        └──> hardware interface read() ──> joint_state_broadcaster
                              │                 └──> /joint_state_broadcaster/joint_states
                              └──> SIM_FULL_STATE_TOPIC (vérité terrain, toutes les liaisons)

    five_bars_state_updater : (q1, q4) ──MuJoCo, fermeture de chaîne──> /joint_states complet
                              ──> robot_state_publisher ──> TF ──> RViz
"""

COMMAND_TOPIC = "/five_bars/joint_commands"
SIM_ACTUATED_STATE_TOPIC = "/five_bars/sim/actuated_joint_states"
SIM_FULL_STATE_TOPIC = "/five_bars/sim/joint_states"
SIM_PEN_TOPIC = "/five_bars/sim/pen_position"
JSB_STATE_TOPIC = "/joint_state_broadcaster/joint_states"
FULL_JOINT_STATES_TOPIC = "/joint_states"
PEN_TOPIC = "/five_bars/pen_position"
BASE_FRAME = "base"
