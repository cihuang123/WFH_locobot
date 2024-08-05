#!/usr/bin/env python3
# the 1/4 below-right Screenshot 
# and publish as ROS topic 
# Editor: Isabella Huang

import rospy
import rospkg
import pyautogui
import cv2
import numpy as np
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge

class ScreenshotNode(object):
    def __init__(self):
        self.node_name = rospy.get_name()
        rospy.loginfo("[%s] Initializing " %(self.node_name))  
        self.screen_width = rospy.get_param("~screen_width", 1280)
        self.screen_height = rospy.get_param("~screen_height", 800)
        self.width, self.height = int(self.screen_width/2), int(self.screen_height/2) 
        self.screenshot_pub = rospy.Publisher("/screenshot", CompressedImage, queue_size=10)
        
        self.bridge = CvBridge()

    def cb(self, no_use):
        img = self.get_screenshot()
        img_msg = self.bridge.cv2_to_compressed_imgmsg(img)
        self.screenshot_pub.publish(img_msg)
        cv2.destroyAllWindows()  
   
    def get_screenshot(self):
        myScreenshot = pyautogui.screenshot(region=(self.width, self.height, 1280, 800))
        image_np = np.array(myScreenshot)
        image_np_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)
        # cv2.imshow("Screenshot", image_np_bgr)

        return image_np_bgr
    
    def on_shutdown(self):
        cv2.destroyAllWindows()  
        rospy.loginfo("[%s] Shutdown " %(self.node_name))
    
if __name__ == "__main__":
    rospy.init_node("screenshot_node", anonymous=False)
    screenshot_node = ScreenshotNode()
    rospy.on_shutdown(screenshot_node.on_shutdown)

    while not rospy.is_shutdown():
        screenshot_node.cb(None)

    rospy.spin()