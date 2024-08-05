#! /bin/bash

# load pyrobot env
load_pyrobot_env
# source WFH workspace and set_rospkg_path
source set_ip.sh
#source ROS/catkin_ws/devel/setup.bash 
#source  ROS/catkin_ws/devel_isolated/setup.bash
source set_rospackage_path.sh
echo "finish setup WFH env"
