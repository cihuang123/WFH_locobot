#!/usr/bin/env python3  
import roslib
import rospy
 
import tf
import turtlesim.msg
from geometry_msgs.msg import PoseStamped

def handle_pose(msg): #callback
    br = tf.TransformBroadcaster()
    br.sendTransform((msg.pose.position.x, msg.pose.position.y, msg.pose.position.z),
                    (msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w),
                    rospy.Time.now(),
                    "object",
                    "camera_color_optical_frame")
 
if __name__ == '__main__':
    rospy.init_node('dope_tf_broadcaster')
    rospy.Subscriber('dope/pose_sugar',
                    PoseStamped,
                    handle_pose)
    rospy.spin()
