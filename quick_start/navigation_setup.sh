#! /bin/bash
source ~/WFH_locobot/environment.sh
source ~/WFH_locobot/set_ip.sh $1 $2
rosservice call /calibration
roslaunch realsense2_camera navigation_camera.launch
