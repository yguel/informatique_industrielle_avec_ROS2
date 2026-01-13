#!/usr/bin/env python3
"""
Launch file for pantographe robot visualization.
Starts robot_state_publisher, joint_state_publisher_gui, and rviz2.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro


def generate_launch_description():

    pkg_path = get_package_share_directory('pantographe_description')
    xacro_path = os.path.join(pkg_path, 'urdf', 'pantographe.urdf')
    rviz_config_path = os.path.join(pkg_path, 'rviz', 'view.rviz')

    # Process xacro file directly
    robot_description = xacro.process_file(xacro_path).toxml()

    return LaunchDescription([
        # Robot State Publisher: publishes /tf and /tf_static from robot_description
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[
                {'robot_description': robot_description},
                {'use_sim_time': False}
            ]
        ),

        # Joint State Publisher GUI: allows manual joint control via sliders
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        ),

        # RViz2: visualization tool
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_path] if os.path.exists(rviz_config_path) else []
        )
    ])

