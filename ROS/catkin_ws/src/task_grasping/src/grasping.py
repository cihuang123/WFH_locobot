#!/usr/bin/env python3

import rospy
import numpy as np
import tf
import time
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import Float64, Empty
from pyrobot import Robot



class task_grasping():
	def __init__(self):
		self.robot = Robot('locobot')
		self.listener = tf.TransformListener()
		# self.pub_gripper_left = rospy.Publisher('/joint_6_cntrl/command', Float64, queue_size=1)
		# self.pub_gripper_right = rospy.Publisher('/joint_7_cntrl/command', Float64, queue_size=1)
		self.pub_grip_open = rospy.Publisher('/gripper/open', Empty, queue_size=1)
		self.pub_grip_close = rospy.Publisher('/gripper/close', Empty, queue_size=1)
		self.pub_cmd_vel = rospy.Publisher('/cmd_vel_mux/input/teleop', Twist, queue_size=1)

		self.robot.camera.set_pan_tilt(0, 0.7, wait=True)
		self.robot.arm.go_home()
		time.sleep(1)
		self.robot.arm.set_joint_positions([1.5, 0.5, -0.5, 0, 0], plan=False)
		self.gripper_open()


		# self.goal_list = ['/dope/pose_sugar', '/dope/pose_mustard', '/dope/pose_meat' ]
		self.id = 0
		print('task_grasping init done')

	def gripper_open(self):
		self.pub_grip_open.publish()
		# self.pub_gripper_left.publish(-0.05)
		# self.pub_gripper_right.publish(0.05)

	def gripper_close(self):
		self.pub_grip_close.publish()
		# self.pub_gripper_left.publish(-0.035)
		# self.pub_gripper_right.publish(0.035)


	def grasping(self):
		#print('goal:',self.goal_list[(self.id%3)], '  times:',self.id)
		try:
			# msg = rospy.wait_for_message(self.goal_list[(self.id%3)], PoseStamped, timeout=5)
			msg = rospy.wait_for_message('/dope/pose_Waterproof', PoseStamped, timeout=5)
		except:
			print('fail to receive message ', self.goal_list[(self.id%3)])
			self.id += 1
			return


		base_link_pose = self.transform_pose(msg.pose, 'base_link', msg.header.frame_id ) # camera_color_optical_frame
		# move base
				#if base_link_pose.pose.position.y > 0.05 :
		#	cmd_vel = Twist()
		#	cmd_vel.angular.z = 0.1
		#	self.pub_cmd_vel.publish(cmd_vel)
		#	print('trun left')
		#	return

		
				#elif base_link_pose.pose.position.y < -0.05 :
		#	cmd_vel = Twist()
		#	cmd_vel.angular.z = -0.1
		#	self.pub_cmd_vel.publish(cmd_vel)
		#	print('trun right')
		#	return

		#cmd_vel = Twist()
		#cmd_vel.angular.z = 0
				#self.pub_cmd_vel.publish(cmd_vel)
		#print('ok, start grasping !!!')
				# move base end

		end_p0 = self.transform_pose(msg.pose, 'base_link', msg.header.frame_id )
		end_p1 = self.transform_pose(msg.pose, 'base_link', msg.header.frame_id )
		end_p0.pose.position.x = end_p0.pose.position.x - 0.233#0.35
		end_p0.pose.position.y = end_p0.pose.position.y + 0.03
		end_p0.pose.position.z = end_p0.pose.position.z + 0.25#0.5
		end_p1.pose.position.x = end_p1.pose.position.x - 0.015#0.4
		end_p1.pose.position.y = end_p1.pose.position.y + 0.03
		end_p1.pose.position.z = end_p1.pose.position.z + 0.08#0.32

		if end_p0==None or end_p0==None:
			print("None")
			return
		target_poses = [{'position': np.array([end_p0.pose.position.x, end_p0.pose.position.y, end_p0.pose.position.z]),\
						 'pitch': 0.73,\
						 'roll': 0.1,\
						 'numerical': True},\
						{'position': np.array([end_p1.pose.position.x, end_p1.pose.position.y, end_p1.pose.position.z]),\
						 'pitch': 0.73 ,\
						 'roll': 0.1,\
						 'numerical': True}]
		print('Go grasp')
		for pose in target_poses:
			try:
				self.robot.arm.set_ee_pose_pitch_roll(**pose)
			except :
				print('fail QAQ')
				return
			time.sleep(0.1)

		self.gripper_close()
		print('gripper close !!')
		target_poses = [{'position': np.array([end_p1.pose.position.x - 0.075, end_p1.pose.position.y, end_p1.pose.position.z + 0.375]),\
						 'pitch': 0.73,\
						 'roll': 0.1,\
						 'numerical': True}]
		for pose in target_poses:
			try:
				self.robot.arm.set_ee_pose_pitch_roll(**pose)
			except :
				print('fail QAQ')
				return
			time.sleep(0.1)

		# self.gripper_open()
		# print('gripper open')
		time.sleep(1)
		self.robot.arm.set_joint_positions([1.5, 0.5, -0.5, 0, 0], plan=False)
		print('go init pose')
		self.id += 1
		end_p0, end_p1 = None, None
		self.gripper_open()



	def transform_pose(self, pose, target_frame, source_frame): #listener
		try:
			(trans_c, rot_c) = self.listener.lookupTransform(
				target_frame, source_frame, rospy.Time(0))
		except (tf.Exception, tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
			rospy.logerr("faile to catch tf %s 2 %s" %
						 (target_frame, source_frame))
			return

		trans_mat = tf.transformations.translation_matrix(trans_c)
		rot_mat = tf.transformations.quaternion_matrix(rot_c)
		tran_mat = np.dot(trans_mat, rot_mat)

		target_mat = np.array([[1, 0, 0, pose.position.x],
							   [0, 1, 0, pose.position.y],
							   [0, 0, 1, pose.position.z],
							   [0, 0, 0, 1]])
		target = np.dot(tran_mat, target_mat)
		quat = tf.transformations.quaternion_from_matrix(target)
		trans = tf.transformations.translation_from_matrix(target)

		t_pose = PoseStamped()
		t_pose.header.frame_id = target_frame
		t_pose.pose.position.x = trans[0]
		t_pose.pose.position.y = trans[1]
		t_pose.pose.position.z = trans[2]
		t_pose.pose.orientation.x = quat[0]
		t_pose.pose.orientation.y = quat[1]
		t_pose.pose.orientation.z = quat[2]
		t_pose.pose.orientation.w = quat[3]

		return t_pose

if __name__=="__main__":
	rospy.init_node("task_grasping")
	task_grasping = task_grasping()
	while not rospy.is_shutdown():
		task_grasping.grasping()
