#! /usr/bin/env python

import rospy
import numpy as np
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped, Pose
import tf
from tf import TransformListener, TransformerROS
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist, Vector3
from nav_msgs.msg import Path
import datetime
import csv
class Path(object):
	def __init__(self):
		self.listener = TransformListener()
		self.pub_pose = rospy.Publisher("gripper_link_pose", PoseStamped, queue_size=1)
		self.timer = rospy.Timer(rospy.Duration(0.2), self.cb_timer)
		self.pub_path = rospy.Publisher('path', Path, queue_size=1)
		self.path = Path()
		self.path.header.frame_id = 'base_link'
		self.count = 0
		self.filename = str(datetime.datetime.now())+'.csv'
		self.list = []
		self.list.append(["header.stamp",\
							"position.x", \
							"position.y", \
							"position.z", \
							"orientation.x", \
							"orientation.y", \
							"orientation.z", \
							"orientation.w"])

	def cb_timer(self,event):
		try:
			(trans,rot) = self.listener.lookupTransform('base_link','gripper_link', rospy.Time(0))
		except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException)as e:
			print(e)
			return

		gripper_pose = PoseStamped()
		gripper_pose.header.frame_id = "gripper_link"
		gripper_pose.pose.position.x = 0
		gripper_pose.pose.position.y = 0
		gripper_pose.pose.position.z = 0
		gripper_pose.pose.orientation.x = 0
		gripper_pose.pose.orientation.y = 0
		gripper_pose.pose.orientation.z = 0
		gripper_pose.pose.orientation.w = 1
		base_link_gripper_pose = self.listener.transformPose('base_link', gripper_pose)


		base_link_gripper_pose.header.stamp = rospy.Time.now()
		base_link_gripper_pose.header.frame_id = "base_link"
		self.pub_pose.publish(base_link_gripper_pose)
		rospy.loginfo("pub posestamp")

		rospy.loginfo('pose marker%d' % self.count)
		self.path.header.stamp = rospy.Time.now()

		pose = PoseStamped()
		self.path.poses.append(base_link_gripper_pose)
		self.pub_path.publish(self.path)
		self.count += 1
		print("pub path",len(self.path.poses))

		self.list.append([base_link_gripper_pose.header.stamp, \
							base_link_gripper_pose.pose.position.x, \
							base_link_gripper_pose.pose.position.y, \
							base_link_gripper_pose.pose.position.z, \
							base_link_gripper_pose.pose.orientation.x, \
							base_link_gripper_pose.pose.orientation.y, \
							base_link_gripper_pose.pose.orientation.z, \
							base_link_gripper_pose.pose.orientation.w,])
		with open(self.filename, 'w') as csvFile:
			writer = csv.writer(csvFile)
			for i in range(len(self.list)): writer.writerow(self.list[i])
		# time.sleep(0.05)


if __name__ == "__main__":
	rospy.init_node("Collector")
	path = Path()
	rospy.spin()

