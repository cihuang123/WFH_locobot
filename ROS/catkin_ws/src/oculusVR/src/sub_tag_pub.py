#!/usr/bin/env python
import rospy
import tf
import std_msgs.msg
from geometry_msgs.msg import PoseArray,PoseStamped,Pose
from apriltags_ros.msg import AprilTagDetection,AprilTagDetectionArray

class tag_detection():
    def __init__(self):
        self.sub_tag = rospy.Subscriber("/tag_detections", AprilTagDetectionArray, self.cb_tag, queue_size=1)
        self.pub_tag = rospy.Publisher("/tagpose", PoseStamped, queue_size=1)

    def cb_tag(self,msg_tag):
	#data type
	tag_dec = AprilTagDetection()
        tag_pos = PoseStamped()
#	tag_pos_ar = PoseArray()
	aList = []

        tag_dec = msg_tag.detections
	for i in range (1,len(tag_dec)):
	    	if (tag_dec[i].id == 0):
			tag_pos = tag_dec[i].pose
			print(tag_pos)
			self.pub_tag.publish(tag_pos)

#	for j in range (0,15): #no.of id
#		for i in range(1,len(tag_dec)):
#	    		if (tag_dec[i].id == j):
#				print(tag_dec[i].id)
#				tag_pos = tag_pose[i].pose
#				aList.append(tag_dec[i].id)
#				print(aList)
				#aList.clear()
				#print(aList)
#				tag_pos_ar[] = tag_pos

	

if __name__=="__main__":
    rospy.init_node("tag")
    tag = tag_detection()
    rospy.spin()
