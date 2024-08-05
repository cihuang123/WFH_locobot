#!/usr/bin/env python
import rospy
import rospkg
import os
import tf
import math
import numpy as np
import time
from std_srvs.srv import Trigger, TriggerResponse
from sensor_msgs.msg import JointState
from std_msgs.msg import Int8
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped, Pose
from pyrobot import Robot
import csv

class Record():
	def __init__(self,number,fps):
		self.robot = Robot('locobot')
        # parameter
		self.number = number
		self.trigger = None
		self.grasped_info = None
		self.joint_info = None
		self.gripper_pose = None
		self.base2gripper_pose = None
		self.count = 0
		self.nu = 1
		self.joint_path = Path()
		self.joint_path.header.frame_id = 'base_link'

		# save path
		r = rospkg.RosPack()
		self.path = os.path.join(r.get_path('locobot_trajectory_log'), "log")
		if not os.path.exists(self.path):
			os.makedirs(self.path)

        # service
		start = rospy.Service("/start_record", Trigger, self.start)
		stop = rospy.Service("/stop_record", Trigger, self.stop)

	# subscriber
		joint = rospy.Subscriber('/joint_states', JointState, self.joint_callback)
		grasped = rospy.Subscriber('/gripper/state', Int8, self.grasped_callback)

	# Publisher
		self.pub_pose = rospy.Publisher("/gripper_link_pose", PoseStamped, queue_size=1)
		self.pub_path = rospy.Publisher('/path', Path, queue_size=1)

	# tf
		self.listener = tf.TransformListener()

	# frame per sec
		delay = 1/float(fps)

	# save data
		self.timer = rospy.Timer(rospy.Duration(delay), self.cb_timer)
	

		print("record ready")
	
	def Is_path_exists(self, path):
		if not os.path.exists(path):
			os.makedirs(path)

	
	
	def start(self, req):
		res = TriggerResponse()
		try:
			self.trigger = True
			res.success = True
			self.number += 1
			self.nu = 1
			res.success = True
		except (rospy.ServiceException, rospy.ROSException) as e:
			res.success = False
			print("Service call failed: %s"%e)
		return res
	
	
	def stop(self, req):
		res = TriggerResponse()
		try:
			self.clear_path()
			self.count = 0
			self.trigger = False
			res.success = True
		except (rospy.ServiceException, rospy.ROSException) as e:
			res.success = False
			print("Service call failed: %s"%e)
		return res   

	def grasped_callback(self, msg):
		self.grasped_info = msg.data

	def joint_callback(self, msg):
		self.joint_info = msg.position[0:7]
	
	def get_base2gripper_posestamped(self,ti):

		try:
			(trans,rot) = self.listener.lookupTransform('base_link','gripper_link', rospy.Time(0))
		except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException)as e:
			print(e)
			return
		gripper_pose = PoseStamped()
		gripper_pose.header.frame_id = "gripper_link" #from_link
		gripper_pose.pose.position.x = 0
		gripper_pose.pose.position.y = 0
		gripper_pose.pose.position.z = 0
		gripper_pose.pose.orientation.x = 0
		gripper_pose.pose.orientation.y = 0
		gripper_pose.pose.orientation.z = 0
		gripper_pose.pose.orientation.w = 1
		
		self.base2gripper_pose = self.listener.transformPose('base_link', gripper_pose) #to_link
		self.base2gripper_pose.header.stamp = ti
		self.base2gripper_pose.header.frame_id = "base_link" #new_frame
		# data of path
		self.pub_pose.publish(self.base2gripper_pose)
		#rospy.loginfo("pub posestamp")

	def draw_path(self,ti):
		rospy.loginfo('pose marker%d' % self.count)
		self.joint_path.header.stamp = ti
		pose = PoseStamped()
		self.joint_path.poses.append(self.base2gripper_pose)
		self.pub_path.publish(self.joint_path)
		self.count += 1
		print("pub path",len(self.joint_path.poses))

	def clear_path(self):
		del self.joint_path.poses[:]
		print(len(self.joint_path.poses))


	def writer_joint_csv(self, path, file_name, data, ti):
		dic = {}
		joint = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6', 'joint7']
		if len(data) != 2:
			for i in range(7):
				dic[joint[i]] = data[i]
		dic['timestamp'] = ti
		joint.append('timestamp')
		self.joint_list = []
		self.joint_list.append(dic)
			
		with open(os.path.join(path, file_name + '.csv'), 'a') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames = joint)
			if self.nu == 1:
				writer.writeheader()
				writer.writerows(self.joint_list)


	def writer_gra_csv(self, path, file_name, data, ti):

		dic = {}
		grasp = ['grasped_info', 'timestamp']
		dic['timestamp'] = ti
		dic['grasped_info'] = data
		self.grasped_list = []
		self.grasped_list.append(dic)
		
		with open(os.path.join(path, file_name + '.csv'), 'a') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames = grasp)
			if self.nu == 1:
				writer.writeheader()
			writer.writerows(self.grasped_list)

	def writer_base2gripper_pose_csv(self, path, file_name, data, ti):
		dic = {}
		gripper_pose = ['header.stamp', \
				"position.x", \
				"position.y", \
				"position.z", \
				"orientation.x", \
				"orientation.y", \
				"orientation.z", \
				"orientation.w"]
		dic['header.stamp'] = data.header.stamp
		dic['position.x'] = data.pose.position.x
		dic['position.y'] = data.pose.position.y
		dic['position.z'] = data.pose.position.z
		dic['orientation.x'] = data.pose.orientation.x
		dic['orientation.y'] = data.pose.orientation.y
		dic['orientation.z'] = data.pose.orientation.z
		dic['orientation.w'] = data.pose.orientation.w

		#print(dic)
		
		with open(os.path.join(path, file_name + '.csv'), 'a') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames = gripper_pose)
			if self.nu == 1:
				writer.writeheader()
			writer.writerows([dic])
	def cb_timer(self,event):
	
		time = rospy.Time.now()
		timestamp = str(time)
		
		self.get_base2gripper_posestamped(time)
		
		if self.trigger:
			# self.draw_path(time)
			log_path = os.path.join(self.path, "log_{:03}".format(self.number))
			self.Is_path_exists(log_path)

			rospy.loginfo('Start collect data!')

			self.writer_base2gripper_pose_csv(log_path, "base2gripper_pose", self.base2gripper_pose, timestamp)
			self.writer_joint_csv(log_path, "joint_info", self.joint_info, timestamp)
			self.writer_gra_csv(log_path, "grasped_info", self.grasped_info, timestamp)
		

		# time.sleep(0.05)

if __name__ == '__main__':
    rospy.init_node('tf_listener')
    number = rospy.get_param("number",0)
    fps = rospy.get_param("fps",10)
    Recoder = Record(number, fps)

    rospy.spin()



