#! /bin/bash

source ~/low_cost_ws/devel/setup.bash
roslaunch locobot_control main.launch use_base:=true use_arm:=true use_camera:=true use_rviz:=false
