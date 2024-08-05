#!/usr/bin/env python3  
import roslib
import rospy
import math
import tf
import geometry_msgs.msg
from std_msgs.msg import Float32MultiArray

def callback(dope_target_position,dope_target_rotation):
    # rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)

def listener():
    rospy.init_node('dope_arm', anonymous=True)

    position_sub = message_filters.Subscriber('dope_target_position',Float32MultiArray)
    rotation_sub = message_filters.Subscriber('dope_target_rotation',Float32MultiArray)
    ts = message_filters.ApproximateTimeSynchronizer([position_sub, rotation_sub], 10, 0.1, allow_headerless=True)
    ts.registerCallback(callback)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
