#!/usr/bin/env python3  
import roslib
import rospy
import math
import tf
import geometry_msgs.msg
from std_msgs.msg import Float32MultiArray

if __name__ == '__main__':
    rospy.init_node('tf_listener')

    listener = tf.TransformListener()

    rate = rospy.Rate(10.0)
    while not rospy.is_shutdown():
        try:
            (trans,rot) = listener.lookupTransform('arm_base_link', 'object', rospy.Time(0))
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            # print("no tf")
            continue
        # print(trans)
        # print(rot)
        pubs = rospy.Publisher('position', Float32MultiArray, queue_size=10)
        pubr = rospy.Publisher('rotation', Float32MultiArray, queue_size=10)

        trans_msg = Float32MultiArray()
        rot_msg = Float32MultiArray()

        trans_msg.data = trans
        rot_msg.data = rot

        pubs.publish(trans_msg)
        pubr.publish(rot_msg)

        # rate.sleep()
