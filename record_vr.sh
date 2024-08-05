#! /bin/bash
mkdir /home/$USER/WFH_locobot/bags/$(date +%m%d_%H%M)

rosbag record -o /home/sis/WFH_locobot/bags/$(date +%m%d_%H%M)/vr --split --size=2048 \
    /joint_states \
    /gripper/state \
    /tf \
    /tf_static 