#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float32MultiArray
import subprocess
import time

class Bandwidth_node(object):
    def __init__(self):
        self.node_name = rospy.get_name()
        rospy.loginfo("[%s] Initializing " %(self.node_name))
        self.veh = rospy.get_param("~veh", "locobot")
        self.bw_pub = rospy.Publisher(self.veh+'/rtx', Float32MultiArray, queue_size=10)
        self.interface = rospy.get_param("~interface", "wlp58s0")
        
        self.update_interval = 0.5
        self.rate = rospy.Rate(1)  # Set the rate to 1 Hz

    def cb(self, no_use):
        rtx = self.get_bw()
        rtx_msg = Float32MultiArray()
        rtx_msg.data = rtx
        print("rtx: ", rtx)

        self.bw_pub.publish(rtx_msg)
        self.rate.sleep()  # Use rate.sleep() to control the loop frequency

    def get_bw(self):
        command = ['ifstat', '-i', self.interface, str(self.update_interval)]
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)
            output = process.stdout.readline()

        # Read the third line of output
            for _ in range(3):
                output = process.stdout.readline()

        # Split the string and convert to float
            rtx = [float(val) for val in output.strip().split()]
            process.terminate()  # Terminate the subprocess

            return rtx
        

        except KeyboardInterrupt:
            # If the user interrupts the program, terminate the subprocess
            if process and process.poll() is None:
                process.terminate()
                process.wait()

        except Exception as e:
            rospy.logerr("Error in get_bw: %s", str(e))
            if process and process.poll() is None:
                process.terminate()
                process.wait()

            return []
            

    def onShutdown(self):
        rospy.loginfo("[%s] Shutdown " %(self.node_name))


if __name__ == "__main__":
    rospy.init_node("bandwidth_node", anonymous=False)
    bandwidth_node = Bandwidth_node()
    rospy.on_shutdown(bandwidth_node.onShutdown)

    while not rospy.is_shutdown():
        bandwidth_node.cb(None)

    rospy.spin()