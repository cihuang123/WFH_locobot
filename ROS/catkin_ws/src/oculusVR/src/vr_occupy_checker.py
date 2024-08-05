#!/usr/bin/env python
import rospy
from std_msgs.msg import Bool
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
import time

class occupy_peeker():
    def __init__(self):
        self.pub_velocity = rospy.Publisher("/cmd_vel/mux/teleop", Twist, queue_size=1)
        self.sub_joycmd_unity = rospy.Subscriber("/vr_joy_cmd", Joy, self.joycmd_unity_callback, queue_size=10)
        self.occupy_id = -1
        self.twist_data = Twist()
        self.time_get_data = time.time()
        
	
    def joycmd_unity_callback(self, msg):
        if self.occupy_id == -1:
            self.occupy_id = msg.axes[0]
            self.twist_data.linear.x = msg.axes[1]
            self.twist_data.angular.z = msg.axes[2]
            self.time_get_data = time.time()
            print("Occupying by id: ", self.occupy_id)
        elif self.occupy_id == msg.axes[0]:
            self.twist_data.linear.x = msg.axes[1]
            self.twist_data.angular.z = msg.axes[2]
            self.time_get_data = time.time()
            print("Occupying by id: ", self.occupy_id)
        else:
            pass
    
    def refresh(self):
        if time.time() - self.time_get_data > 0.5:
            self.occupy_id = -1
            self.twist_data.linear.x = 0
            self.twist_data.angular.z = 0
            print("No occupy")
        else:
            pass

if __name__ == "__main__":
    rospy.init_node("occupy_peeker")
    occupy_check = occupy_peeker()
    while not rospy.is_shutdown():
        occupy_check.refresh()
        occupy_check.pub_velocity.publish(occupy_check.twist_data)
        rospy.sleep(0.1)