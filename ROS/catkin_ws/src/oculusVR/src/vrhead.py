#!/usr/bin/env python3
import rospy
import tf
import math
from std_msgs.msg import Float64
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
class subvrandpub(object):
 
    def __init__(self):
        self.sub = rospy.Subscriber("vr/head", PoseStamped, self.callback)
        self.pub_pan = rospy.Publisher('/pan/command', Float64, queue_size=10)
        self.pub_tilt = rospy.Publisher('/tilt/command', Float64, queue_size=10)
        self.pub_planeposition = rospy.Publisher('/plane/position',PoseStamped, queue_size=10)
 
    def callback(self, data):
        explicit_quat = [data.pose.orientation.x, data.pose.orientation.y, data.pose.orientation.z, data.pose.orientation.w]
        your_euler = tf.transformations.euler_from_quaternion(explicit_quat)
        #print(data)
        print(your_euler)
        #unity
        x = 9*math.sin(your_euler[2])*math.cos(your_euler[1])
        y = -5*9*math.sin(-your_euler[2])*math.sin(your_euler[1])
        z = 9*math.cos(your_euler[2])
 
        planeposition=PoseStamped()
        planeposition.pose.position.x = z
        planeposition.pose.position.y = x
        
        planeposition.pose.position.z = y
        planeposition.pose.orientation.x = 0.70710682869
        planeposition.pose.orientation.y = 0
        planeposition.pose.orientation.z = -0.70710682869
        planeposition.pose.orientation.w = 0
        #print("plane",planeposition)

        #locobot
        self.pub_pan.publish(your_euler[2])
        self.pub_tilt.publish(your_euler[1])
        #unity
 
        self.pub_planeposition.publish(planeposition)
if __name__ == '__main__':
    rospy.init_node('listener', anonymous=True)
    SUB = subvrandpub()
    rospy.spin() #run forever
