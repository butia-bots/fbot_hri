from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    return LaunchDescription([
        Node(name='audio_player', 
             package='fbot_speech', 
             executable='audio_player.py',
             parameters=[PathJoinSubstitution(FindPackageShare('fbot_hri_bringup'), 'config', 'ros.yaml'), 
                         PathJoinSubstitution(FindPackageShare('fbot_hri_bringup'), 'config', 'fbot_audio_player.yaml'), 
                         ]
            ),
        Node(name='speech_synthesizer', 
             package='fbot_speech', 
             executable='speech_synthesizer_old.py',
             parameters=[PathJoinSubstitution(FindPackageShare('fbot_hri_bringup'), 'config', 'ros.yaml'), 
                         PathJoinSubstitution(FindPackageShare('fbot_hri_bringup'), 'config', 'fbot_speech_synthesizer_old.yaml'), 
                         ]
            ),
    ])