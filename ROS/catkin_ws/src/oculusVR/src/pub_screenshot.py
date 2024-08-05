#!/usr/bin/env python3
#this code is for capture the view of window and publish it to ROS topic
#check the screen_crop_rviz.launch for setup the parameters
#capture_window is the window name you want to capture (you can use wmctrl -lGx to check the window name e.g. rviz.rviz or default.rviz* - RViz)
#start_x_offset, start_y_offset, end_x_offset, end_y_offset are the offset of the window you want to crop th UI)
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import subprocess
import re
import numpy as np
import cv2
from PIL import ImageGrab

class WindowCapturePublisher:
    def __init__(self, window_title, topic_name, start_x_offset=0, start_y_offset=0, end_x_offset=0, end_y_offset=0):
        self.window_title = window_title
        self.topic_name = topic_name
        self.pub = rospy.Publisher(topic_name, Image, queue_size=10)
        self.bridge = CvBridge()
        self.start_x_offset = start_x_offset
        self.start_y_offset = start_y_offset
        self.end_x_offset = end_x_offset
        self.end_y_offset = end_y_offset

    def get_window_geometry(self):
        try:
            if self.window_title == 'Navigator.Firefox': # if wmctrl capture the wrong window, use xdotool
                window_id = subprocess.check_output(['xdotool', 'search', '--name', self.window_title]).decode().strip()
                geometry_output = subprocess.check_output(['xdotool', 'getwindowgeometry', window_id]).decode()
                print("xdotool output:\n", geometry_output)  # Debugging line
                x = int(re.search(r'Position: (\d+),(\d+)', geometry_output).group(1))
                y = int(re.search(r'Position: (\d+),(\d+)', geometry_output).group(2))
                width = int(re.search(r'Geometry: (\d+)x(\d+)', geometry_output).group(1))
                height = int(re.search(r'Geometry: (\d+)x(\d+)', geometry_output).group(2))
                return x, y, width, height, 'xdotool'
            else:  # Normal window can be correct capture with wmctrl 
                output = subprocess.check_output(["wmctrl", "-lGx"]).decode()
                print("wmctrl output:\n", output)  # Debugging line
                for line in output.splitlines():
                    if self.window_title in line:
                        print("Matching line found:\n", line)  # Debugging line
                        _,_, x, y, width, height, _ = re.split(r'\s+', line, maxsplit=6)
                        #print(f"Extracted geometry: x={x}, y={y}, width={width}, height={height}")  # Debugging line
                        return int(x), int(y), int(width), int(height), 'wmctrl'
        except subprocess.CalledProcessError as e:
            rospy.loginfo("Could not get window geometry: " + str(e))
        return None
    


    def capture_window(self):
        window_geometry = self.get_window_geometry()
        if window_geometry:
            x, y, width, height, method  = window_geometry
            if method == 'xdotool':
                screenshot = ImageGrab.grab(bbox=(x, y+30, x + width, y + height))
            else:
                screenshot = ImageGrab.grab(bbox=(x-10+self.start_x_offset, y-50+self.start_y_offset, x+width-10-self.end_x_offset, y+height-50-self.end_y_offset)) # you can modify the bbox to crop the window UI
            return screenshot
        else:
            return None

    def publish_image(self):
        while not rospy.is_shutdown():
            screenshot = self.capture_window()
            if screenshot:
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                msg = self.bridge.cv2_to_imgmsg(frame)
                self.pub.publish(msg)
            rospy.Rate(10).sleep()  # Adjust the rate as needed

if __name__ == '__main__':
    rospy.init_node('window_capture_node', anonymous=True)
    # my_capture_window = rospy.get_param('~capture_window', 'QGroundControl Daily')
    # my_capture_window = rospy.get_param('~capture_window', 'Image_map')
    my_capture_window = rospy.get_param('~capture_window', 'Navigator.Firefox')
    start_x_offset = rospy.get_param('~start_x_offset', 0)
    start_y_offset = rospy.get_param('~start_y_offset', 120)
    end_x_offset = rospy.get_param('~end_x_offset', 0)
    end_y_offset = rospy.get_param('~end_y_offset', 0)
    print("start_x_offset: ", start_x_offset, "start_y_offset: ", start_y_offset, "end_x_offset: ", end_x_offset, "end_y_offset: ", end_y_offset)
    
    window_capture_publisher = WindowCapturePublisher(my_capture_window, '/window_capture', start_x_offset, start_y_offset, end_x_offset, end_y_offset)
    window_capture_publisher.publish_image()
