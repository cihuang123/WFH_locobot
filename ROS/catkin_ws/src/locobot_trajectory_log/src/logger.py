#!/usr/bin/env python
import rospy
import rospkg
import os
import time
from std_srvs.srv import Trigger, TriggerResponse
from sensor_msgs.msg import Image
from sensor_msgs.msg import JointState
from std_msgs.msg import Int8
from cv_bridge import CvBridge
import message_filters
import cv2
import numpy as np
import csv

class Collect(object):
    def __init__(self, number, fps):

        # parameter
        self.number = number
        self.trigger = None
        self.grasped_info = None
        self.traj_info = None
        self.rgb = None
        self.depth = None
        self.ex_rgb = None
        self.ex_depth = None
        self.nu = 1
        self.dic = {}

        self.cv_bridge = CvBridge()
        r = rospkg.RosPack()
        self.path = os.path.join(r.get_path('locobot_trajectory_log'), "log")

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        # ros service
        start = rospy.Service("/start_collect", Trigger, self.start)
        stop = rospy.Service("/stop_collect", Trigger, self.stop)

        fps = 10
        delay = 1/float(fps)

        # ros subscriber
        img_rgb = message_filters.Subscriber('/camera/color/image_raw', Image)
        img_depth = message_filters.Subscriber('/camera/aligned_depth_to_color/image_raw', Image)
        ex_img_rgb = message_filters.Subscriber('/ex_side_camera/color/image_raw', Image)
        ex_img_depth = message_filters.Subscriber('/ex_side_camera/aligned_depth_to_color/image_raw', Image)
        self.ts = message_filters.ApproximateTimeSynchronizer([img_rgb, img_depth, ex_img_rgb, ex_img_depth], 10, 1)
        self.ts.registerCallback(self.register)

        traj = rospy.Subscriber('/joint_states', JointState, self.traj_callback)
        grasped = rospy.Subscriber('/gripper/state', Int8, self.grasped_callback)

        # save data
        rospy.Timer(rospy.Duration(delay), self.save)

    def start(self, req):

        res = TriggerResponse()

        try:
            self.trigger = True
            res.success = True
            self.number += 1
            self.nu = 1
        except (rospy.ServiceException, rospy.ROSException) as e:
            res.success = False
            print("Service call failed: %s"%e)
        
        return res

    def stop(self, req):

        res = TriggerResponse()

        try:
            self.trigger = False
            res.success = True
        except (rospy.ServiceException, rospy.ROSException) as e:
            res.success = False
            print("Service call failed: %s"%e)
        
        return res

    def grasped_callback(self, msg):

        self.grasped_info = msg.data

    def traj_callback(self, msg):

        self.traj_info = msg.position[0:7]
        
    def writer_traj_csv(self, path, file_name, data, ti):

        joint = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6', 'joint7']
	if len(data) != 2:
        	for i in range(7):
		    self.dic[joint[i]] = data[i]
	self.dic['timestamp'] = ti
	joint.append('timestamp')
		
	with open(os.path.join(path, file_name + '.csv'), 'a') as csvfile:

	    writer = csv.DictWriter(csvfile, fieldnames = joint)
	    if self.nu == 1:
		writer.writeheader()
	    writer.writerows([self.dic])

    def writer_gra_csv(self, path, file_name, data, ti):

        dic = {}
        title = ['grasped_info', 'timestamp']
        dic['timestamp'] = ti
        dic['grasped_info'] = data
        self.grasped_list = []
        self.grasped_list.append(dic)
        
        with open(os.path.join(path, file_name + '.csv'), 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = title)
            if self.nu == 1:
                writer.writeheader()
            writer.writerows(self.grasped_list)

    def register(self, rgb, depth, ex_rgb, ex_depth):

        self.rgb = self.cv_bridge.imgmsg_to_cv2(rgb, "bgr8")
        self.depth = self.cv_bridge.imgmsg_to_cv2(depth, "16UC1")
        self.depth = np.array(self.depth) / 1000.0

        self.ex_rgb = self.cv_bridge.imgmsg_to_cv2(ex_rgb, "bgr8")
        self.ex_depth = self.cv_bridge.imgmsg_to_cv2(ex_depth, "16UC1")
        self.ex_depth = np.array(self.ex_depth) / 1000.0

    def Is_path_exists(self, path):

        if not os.path.exists(path):
            os.makedirs(path)

    def save(self, event):

	    if self.trigger:

		rospy.loginfo('Start collect data!')

		log_path = os.path.join(self.path, "log_{:03}".format(self.number))
		img_path = os.path.join(log_path, "img")
		dep_path = os.path.join(log_path, "dep")

                top_img_path = os.path.join(img_path, "top")
                top_dep_path = os.path.join(dep_path, "top")

                side_img_path = os.path.join(img_path, "side")
                side_dep_path = os.path.join(dep_path, "side")

                self.Is_path_exists(log_path)
                self.Is_path_exists(img_path)
                self.Is_path_exists(dep_path)
                self.Is_path_exists(top_img_path)
                self.Is_path_exists(top_dep_path)
                self.Is_path_exists(side_img_path)
                self.Is_path_exists(side_dep_path)

		ti = time.time()
		timestamp = str(ti)

		self.writer_traj_csv(log_path, "trajectory_info", self.traj_info, timestamp)
		self.writer_gra_csv(log_path, "grasped_info", self.grasped_info, timestamp)

		img_name = os.path.join(top_img_path, timestamp + "_img.jpg")
		depth_name = os.path.join(top_dep_path, timestamp + "_dep.npy")
                ex_img_name = os.path.join(side_img_path, timestamp + "_ex_img.jpg")
		ex_depth_name = os.path.join(side_dep_path, timestamp + "_ex_dep.npy")
	
		cv2.imwrite(img_name, self.rgb)
		np.save(depth_name, self.depth)
                cv2.imwrite(ex_img_name, self.ex_rgb)
		np.save(ex_depth_name, self.ex_depth)
		self.nu += 1

if __name__ == "__main__":

    rospy.init_node("collect_data_node")

    number = rospy.get_param("number")
    fps = rospy.get_param("fps")
    collecter = Collect(number, fps)
    rospy.spin()
