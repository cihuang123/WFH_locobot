#!/usr/bin/env python

import rospy
import numpy as np
from pyrobot import Robot

def init_arm_and_camera():
    posn = np.asarray(['0.07','0.07','0.9'], dtype=np.float64, order="C")
    bot = Robot("locobot_kobuki", arm_config={"use_moveit": True, "moveit_planner": "ESTkConfigDefault"}, base_config={"base_controller": "ilqr", "base_planner": "none"})
    bot.camera.set_pan_tilt(0, 0.8, wait=True)
    bot.arm.go_home()
    bot.arm.set_joint_positions([1.5, 0.5, 0.3, -0.7, 0.0], plan=False)
    bot.arm.set_joint_positions([1.7, 0.9, 0.3, -1.1, 0.0], plan=False)
    bot.base.go_to_relative(posn, use_map=False, close_loop=True, smooth=True)

if __name__=="__main__":
    
    init_arm_and_camera()
