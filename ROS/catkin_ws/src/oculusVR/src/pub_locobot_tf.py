#!/usr/bin/env python
import roslib
import rospy
import math
import tf
import geometry_msgs.msg
from std_msgs.msg import Float32MultiArray

if __name__ == '__main__':
    rospy.init_node('tf_listener')
    print("ready_tf")
    listener = tf.TransformListener()

    while not rospy.is_shutdown():
        try:
            #listener
            (trans_oa,rot_oa) = listener.lookupTransform('odom','arm_base_link', rospy.Time(0))
            (trans_ac,rot_ac) = listener.lookupTransform('arm_base_link','camera_color_optical_frame', rospy.Time(0))
            (trans_acs,rot_acs) = listener.lookupTransform('arm_base_link','ex_side_camera_color_optical_frame', rospy.Time(0)) # side_tf
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
	    #print("no tf")
            continue

	#from quaternion to euler
#	quat = (rot[0],rot[1],rot[2],rot[3])
#	eular = tf.transformations.euler_from_quaternion(quat)

	#Datatype
        trans_oa_msg = Float32MultiArray()
        rot_oa_msg = Float32MultiArray()
        trans_ac_msg = Float32MultiArray()
        rot_ac_msg = Float32MultiArray()
        trans_acs_msg = Float32MultiArray() #side_camera
        rot_acs_msg = Float32MultiArray()  #side_camera


        #Publisher
        pub_oa_p = rospy.Publisher('tf_oa_position', Float32MultiArray, queue_size=1)
        pub_oa_r = rospy.Publisher('tf_oa_rotation', Float32MultiArray, queue_size=1)
        pub_ac_p = rospy.Publisher('tf_ac_position', Float32MultiArray, queue_size=1)
        pub_ac_r = rospy.Publisher('tf_ac_rotation', Float32MultiArray, queue_size=1)
        #side_camera
        pub_acs_p = rospy.Publisher('tf_acs_position', Float32MultiArray, queue_size=1)
        pub_acs_r = rospy.Publisher('tf_acs_rotation', Float32MultiArray, queue_size=1)


        trans_oa_msg.data = trans_oa
        rot_oa_msg.data = rot_oa
        trans_ac_msg.data = trans_ac
        rot_ac_msg.data = rot_ac
        trans_acs_msg.data = trans_acs #side_camera
        rot_acs_msg.data = rot_acs #side_camera


        pub_oa_p.publish(trans_oa_msg)
        pub_oa_r.publish(rot_oa_msg)
        pub_ac_p.publish(trans_ac_msg)
        pub_ac_r.publish(rot_ac_msg)
        pub_acs_p.publish(trans_acs_msg) #side_camera
        pub_acs_r.publish(rot_acs_msg) #side_camera

        # rate.sleep()
