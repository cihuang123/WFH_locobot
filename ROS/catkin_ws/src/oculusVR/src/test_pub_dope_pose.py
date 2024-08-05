#!/usr/bin/env python  
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from std_msgs.msg import Float32MultiArray

position_msg = Float32MultiArray()
# pose_msg = Pose()

def talker():
    pub = rospy.Publisher('/dope/test', Float32MultiArray, queue_size=10)
    rospy.init_node('dope_pose_test', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    
    while not rospy.is_shutdown():

	#pose_msg.orientation.x = -0.696
	#pose_msg.orientation.y = -0.6420
	#pose_msg.orientation.z = -0.2574
	#pose_msg.orientation.w = 0.1923

        #pose_msg.position.x = 0.09018
        #pose_msg.position.y = 0.07301
        #pose_msg.position.z = 0.73818


        #rospy.loginfo(pose_msg)
        array = [0.09018,0.07301,0.73818,-0.696,-0.6420,-0.2574,] 
        position_msg = Float32MultiArray(data=array)

        rospy.loginfo(position_msg)
        pub.publish(position_msg)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
