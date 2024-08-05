#!/usr/bin/env python2.7
import rospy
from std_srvs.srv import Trigger, TriggerResponse
from sensor_msgs.msg import JointState, CompressedImage
from geometry_msgs.msg import Twist, TwistStamped
from std_msgs.msg import Bool, Int32, Int16, Float64
import time
import statistics
import pandas as pd

class timestamp_img():
    def __init__(self):
        rospy.Subscriber('/publish_topic/compressed', CompressedImage, self.timestamp_callback, queue_size=60)
        # rospy.Subscriber('/publish_topic', Twist, self.timestamp_callback, queue_size=60)
        self.delay_time_count = []
        self.seq = []
        self.list_count = 1500
        self.i = 0

        # self.timestamp_msg = TwistStamped()
        
    def timestamp_callback(self, msg):
        delay = time.time() - msg.header.stamp.secs - msg.header.stamp.nsecs * 1e-9
        # delay = time.time() - msg.linear.x - msg.linear.y * 1e-9
        # print(delay)
        self.delay_time_count.append(delay)
        self.seq.append(msg.header.seq)
        # print(self.delay_time_count)
        self.i += 1
       # print('start log')
        if(self.i == self.list_count):
            self.i = 0
            print("mean RTT", sum(self.delay_time_count)/self.list_count)
            print("max RTT", max(self.delay_time_count))
            print("min RTT", min(self.delay_time_count))
            print("STD RTT", statistics.stdev(self.delay_time_count))
            dict = {
                'seq': self.seq,
                'raw': self.delay_time_count, 
                #'mean':(sum(self.delay_time_count)/self.list_count),
                #'max':max(self.delay_time_count),
                #'min':min(self.delay_time_count),
                #'STD':statistics.stdev(self.delay_time_count)
                }
            df = pd.DataFrame(dict)
            df.to_csv('latency_img_wifi6.csv')
            self.delay_time_count.clear()

if __name__=='__main__':
    rospy.init_node("timestamp_img", anonymous=False)
    class_img = timestamp_img()

    rospy.spin()
