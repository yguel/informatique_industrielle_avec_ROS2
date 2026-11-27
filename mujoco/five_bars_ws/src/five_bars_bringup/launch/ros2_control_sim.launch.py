"""ros2_control + simulateur MuJoCo + mise à jour de l'état complet.

    ros2 launch five_bars_bringup ros2_control_sim.launch.py [gui:=true] [rviz:=true] [use_viewer:=true]

  forward_position_controller --(command interface)--> MujocoTopicSystem.write()
       --/five_bars/joint_commands--> sim_node (MuJoCo)  <--  IHM curseurs (gui:=true)
  sim_node --/five_bars/sim/actuated_joint_states--> MujocoTopicSystem.read()
       --> joint_state_broadcaster --/joint_state_broadcaster/joint_states--> state_updater
       --/joint_states (4 liaisons)--> robot_state_publisher --> TF --> RViz

Envoyer une consigne via ros2_control :
  ros2 topic pub --once /forward_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [2.2, 1.0]}"
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_viewer = LaunchConfiguration("use_viewer")
    gui = LaunchConfiguration("gui")
    rviz = LaunchConfiguration("rviz")
    robot_description = ParameterValue(Command([
        "xacro ", PathJoinSubstitution([FindPackageShare("five_bars_description"), "urdf", "five_bars.urdf.xacro"]),
        " ros2_control:=true"]), value_type=str)
    controllers = PathJoinSubstitution([FindPackageShare("five_bars_bringup"), "config", "controllers.yaml"])

    return LaunchDescription([
        DeclareLaunchArgument("use_viewer", default_value="true", description="viewer 3D MuJoCo"),
        DeclareLaunchArgument("gui", default_value="false", description="IHM curseurs sur le topic de commande"),
        DeclareLaunchArgument("rviz", default_value="false", description="lancer RViz"),
        # Simulateur (processus séparé, piloté par topic)
        Node(package="five_bars_mujoco", executable="sim_node", output="screen",
             parameters=[{"use_viewer": use_viewer}]),
        # robot_description -> /robot_description (lu aussi par le controller_manager)
        Node(package="robot_state_publisher", executable="robot_state_publisher", output="screen",
             parameters=[{"robot_description": robot_description}]),
        Node(package="controller_manager", executable="ros2_control_node", output="screen",
             parameters=[controllers]),
        Node(package="controller_manager", executable="spawner", output="screen",
             arguments=["joint_state_broadcaster", "forward_position_controller",
                        "--controller-manager", "/controller_manager"]),
        Node(package="controller_manager", executable="spawner", output="screen",
             arguments=["joint_trajectory_controller", "--inactive",
                        "--controller-manager", "/controller_manager"]),
        # Étape 4 : état complet de la chaîne fermée
        Node(package="five_bars_mujoco", executable="state_updater", output="screen",
             parameters=[{"input_topic": "/joint_state_broadcaster/joint_states"}]),
        Node(package="five_bars_mujoco", executable="slider_gui", output="screen", condition=IfCondition(gui)),
        Node(package="rviz2", executable="rviz2", output="log", condition=IfCondition(rviz),
             arguments=["-d", PathJoinSubstitution([FindPackageShare("five_bars_bringup"), "rviz", "five_bars.rviz"])]),
    ])
