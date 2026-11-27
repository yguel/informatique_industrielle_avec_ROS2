"""ÉTAPE 3 sans ros2_control : simulateur MuJoCo + IHM curseurs, reliés par topic.

    ros2 launch five_bars_bringup sim_gui.launch.py [rviz:=true] [use_viewer:=true]

IHM --/five_bars/joint_commands--> sim_node --/five_bars/sim/actuated_joint_states--> state_updater
--/joint_states--> robot_state_publisher --> RViz
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
    rviz = LaunchConfiguration("rviz")
    robot_description = ParameterValue(Command([
        "xacro ", PathJoinSubstitution([FindPackageShare("five_bars_description"), "urdf", "five_bars.urdf.xacro"]),
        " ros2_control:=false"]), value_type=str)
    return LaunchDescription([
        DeclareLaunchArgument("use_viewer", default_value="true", description="viewer 3D MuJoCo"),
        DeclareLaunchArgument("rviz", default_value="false", description="lancer RViz"),
        Node(package="five_bars_mujoco", executable="sim_node", output="screen",
             parameters=[{"use_viewer": use_viewer}]),
        Node(package="five_bars_mujoco", executable="slider_gui", output="screen"),
        Node(package="five_bars_mujoco", executable="state_updater", output="screen",
             parameters=[{"input_topic": "/five_bars/sim/actuated_joint_states"}]),
        Node(package="robot_state_publisher", executable="robot_state_publisher", output="screen",
             parameters=[{"robot_description": robot_description}]),
        Node(package="rviz2", executable="rviz2", output="log", condition=IfCondition(rviz),
             arguments=["-d", PathJoinSubstitution([FindPackageShare("five_bars_bringup"), "rviz", "five_bars.rviz"])]),
    ])
