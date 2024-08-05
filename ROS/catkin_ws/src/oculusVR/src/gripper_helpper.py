#!/usr/bin/env python
import rospy
import tf
import math
import numpy as np
import time
from std_msgs.msg import Bool, Float64
from std_srvs.srv import Trigger, TriggerResponse
from pyrobot import Robot

class Gripper():

    def __init__(self):
        self.robot = Robot('locobot')

        # ros service
        opening = rospy.Service("/open_gripper", Trigger, self.open)
        stopping = rospy.Service("/close_gripper", Trigger, self.close)
	print("gripper ready")

    def gripper_close(self):
        print("close")
        self.robot.gripper.close()

    def gripper_open(self):
        print("open")
        self.robot.gripper.open()


    def open(self, req):

        res = TriggerResponse()

        try:
            self.gripper_open()
        except (rospy.ServiceException, rospy.ROSException) as e:
            res.success = False
            print("Service call failed: %s"%e)
        
        return res

    def close(self, req):

        res = TriggerResponse()

        try:
            self.gripper_close()
        except (rospy.ServiceException, rospy.ROSException) as e:
            res.success = False
            print("Service call failed: %s"%e)
        
        return res     
    

if __name__ == '__main__':
    rospy.init_node('gripperhelper')
    test = Gripper()
    rospy.spin()
