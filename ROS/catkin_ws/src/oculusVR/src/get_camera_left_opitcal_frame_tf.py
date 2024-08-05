#!/usr/bin/env python
import rospy
import tf2_ros
import tf2_geometry_msgs
from geometry_msgs.msg import PoseStamped
from std_srvs.srv import Trigger, TriggerResponse
import tf
import math

class object_trans():
    def __init__(self, target_frame, source_frame):
        self.target_frame = target_frame
        self.source_frame = source_frame
        self.buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.buffer)
        get_left_cam_tf = rospy.Service("/get_left_unity", Trigger, self.left_unity)
        
    def quaternion_to_euler(self, quaternion):
    # Convert quaternion to Euler angles
        euler = tf.transformations.euler_from_quaternion((quaternion.x, quaternion.y, quaternion.z, quaternion.w))
        roll, pitch, yaw = euler

        return roll, pitch, yaw

    def left_unity(self, req):
        res = TriggerResponse()
        try:
            transform = self.buffer.lookup_transform(self.target_frame, self.source_frame, rospy.Time(0))
            print('---------------For unity left pc transform--------------------------')
            print("Position")
            print('x = ',-1 * transform.transform.translation.y)
            print('y = ',transform.transform.translation.z)
            print('z = ',transform.transform.translation.x)
            print("Rotation")
            rx,ry,rz = self.quaternion_to_euler(transform.transform.rotation)
            print('x = ',-1 *180/math.pi *rx)
            print('y = ',-1 * 180/math.pi * rz -90)
            print('z = ',180/math.pi * ry )
            res.success = True
        except (rospy.ServiceException, rospy.ROSException) as e:
            res.success = False
            print("Service call failed: %s"%e)

        return res

    
        
        
if __name__ == "__main__":
    rospy.init_node("left_pose_transform", anonymous=False)

    left_cam = object_trans('base_link', 'camera_left_color_optical_frame')
       
    rospy.spin()