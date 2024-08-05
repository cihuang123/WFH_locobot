#!/bin/bash

source ~/WFH_locobot/environment.sh
source ~/WFH_locobot/set_ip.sh $1 $2
roslaunch realsense2_camera cam_ml_wfh60.launch


