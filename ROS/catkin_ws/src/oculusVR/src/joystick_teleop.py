#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

def joy_callback(data):
    # Create a Twist message
    twist = Twist()
    print(data)
    # Set linear x speed based on joystick axes[1]
    # Increasing axes[1] value means more speed forward
    twist.linear.x = 0.3* data.axes[1]

    # Set angular z speed based on joystick axes[0]
    # Positive axes[0] for left rotation, negative for right
    twist.angular.z = data.axes[0]

    # Publish the twist message to the /teleop topic
    pub.publish(twist)

if __name__ == '__main__':
    try:
        # Initialize the ROS node
        rospy.init_node('joy_to_teleop')

        # Create a publisher for the /teleop topic with message type Twist
        pub = rospy.Publisher('/cmd_vel_mux/input/teleop', Twist, queue_size=10)

        # Subscribe to the /joy topic with the callback function
        rospy.Subscriber("/joy", Joy, joy_callback)

        # Keep the program alive
        rospy.spin()
    except rospy.ROSInterruptException:
        pass