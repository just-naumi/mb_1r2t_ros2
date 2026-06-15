#!/usr/bin/env python3
"""
Launch file untuk slam_toolbox dengan driver mb_1r2t_ros2
Platform: Windows 11 + WSL Ubuntu 20.04
ROS Version: ROS 2 Foxy Fitzroy
"""

import os
 
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Path ke file konfigurasi YAML
    config_dir = os.path.join(
        os.path.expanduser('~'),
        'ros2_ws', 'src', 'mb_1r2t_ros2', 'config'
    )
    slam_params_file = os.path.join(config_dir, 'slam_toolbox_params.yaml')

    # Deklarasi argumen
    port_arg = DeclareLaunchArgument(
        'port',
        default_value='/dev/ttyUSB0',
        description='Serial port untuk sensor LiDAR MB-1R2T'
    )

    return LaunchDescription([
        port_arg,

        # 1. Node Driver LiDAR MB-1R2T
        Node(
            package='mb_1r2t',
            executable='mb_1r2t_node',
            name='mb_1r2t_node',
            output='screen',
            parameters=[{
                'port': LaunchConfiguration('port'),
                'frame_id': 'lidar'
            }]
        ),

        # 2. Static Transform Publisher: base_link -> lidar (sensor statis)
        # Parameter: x y z qx qy qz qw frame_id child_frame_id
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_lidar_broadcaster',
            arguments=['0', '0', '0', '0', '0', '0', '1', 'base_link', 'lidar'],
            output='screen'
        ),

        # 3. Tambahan: odom = base_link (tidak ada wheel odometry)
        # Ini memberitahu slam_toolbox bahwa robot tidak bergerak secara odom
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='odom_to_base_broadcaster',
            arguments=['0', '0', '0', '0', '0', '0', '1', 'odom', 'base_link'],
            output='screen'
        ),

        # 4. Node slam_toolbox (Online Async Mode)
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[slam_params_file],
        ),
    ])
