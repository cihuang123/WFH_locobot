#!/usr/bin/env python2
import rospy
import tf
import math
import numpy as np
import time
from std_msgs.msg import Bool, Float64
from sensor_msgs.msg import Joy
from geometry_msgs.msg import PoseStamped, Pose
from sensor_msgs.msg import JointState
from pyrobot import Robot

class subvrcontrollerpub(object):
 
    def __init__(self):
        #Sub
        self.sub_controller= rospy.Subscriber("/vr/controller_position", Pose, self.controller_callback,queue_size=1)  #for position of ee
        self.sub_primary = rospy.Subscriber("/vr/primarybutton", Bool, self.primarybutton_callback,queue_size=1)	#gripper open
        self.sub_second = rospy.Subscriber("/vr/secondarybutton", Bool, self.secondarybutton_callback,queue_size=1)	#gripper close
        self.sub_joystick = rospy.Subscriber("/vr/joystick", Joy, self.joystick_callback,queue_size=1)	#for rotation of ee
        self.sun_jointstate = rospy.Subscriber("/joint_states", JointState, self.jointstate_callback,queue_size=10) #for current joint state
	#Pub
        
        self.robot = Robot('locobot')
        self.arm_wake()
        print('init done')

    def arm_wake(self):
        print("arm wake")
        target_poses = [
                {"position": np.array([0.28, 0, 0.22]),
                    "pitch": 0.5,
                    "roll": 0.5,
                    "numerical": False
                    }
                ]
        for pose in target_poses:
            self.robot.arm.set_ee_pose_pitch_roll(plan=True, **pose)
            time.sleep(1)


    def gripper_close(self):
        print("close")
        self.robot.gripper.close()

    def gripper_open(self):
        print("open")
        self.robot.gripper.open()

    def primarybutton_callback(self, msg_close):
        p_close = msg_close.data
        #print("primary", p_close)
        if (p_close == True):
            self.gripper_close()
    
    def secondarybutton_callback(self, msg_open):
        p_open=msg_open.data
        #print("second",  p_open)
        if (p_open == True):
            self.gripper_open()

    def controller_callback(self, msg_controller):
        print("controller")
        controller_pos = Pose()
        controller_pos = msg_controller

        #Get position
        position_x = round(controller_pos.position.x,2)
        position_y = round(controller_pos.position.y,2)
        position_z = round(controller_pos.position.z,2)

        #Get rotation
        rotation_x = round(controller_pos.orientation.x,4)
        rotation_y = round(controller_pos.orientation.y,4)
        rotation_z = round(controller_pos.orientation.z,4)
        rotation_w = round(controller_pos.orientation.w,4)

        ##from quaternion to euler##
        quat = (rotation_x,rotation_y,rotation_z,rotation_w)
        euler = tf.transformations.euler_from_quaternion(quat)
        
        #print("position: ",position_x,position_y,position_z)
        #print("rotation(q): ",rotation_x,rotation_y,rotation_z,rotation_w)
        #print("rotation(e): ",eular[0],eular[1],eular[2])

        target_poses = [
                {"position": np.array([position_x,position_y,position_z]), 
                    "pitch": euler[1], 
                    "roll": euler[0], 
                    "numerical": False
                    }
        #{"position": np.array([position_x,position_y,position_z]),
        #    "orientation": np.array([0.924,0,-0.383,0]),
        #    }
        ]
        for pose in target_poses:
        #    self.robot.arm.set_ee_pose(plan=True, **pose)
            self.robot.arm.set_ee_pose_pitch_roll(plan=True, **pose)
            time.sleep(1)

        print("finish")
   	

    def joystick_callback(self,joy_data):
        joystick = Joy()
        joystick = joy_data
        
        _joint = self.joint
        #print(_joint.position[0]) #check
        joint_1 = _joint.position[0]
        joint_2 = _joint.position[1]
        joint_3 = _joint.position[2]
        joint_4 = _joint.position[3]
        joint_5 = _joint.position[4]
        joint_6 = _joint.position[5]
        joint_7 = _joint.position[6]
        #print(joint_1,joint_2,joint_3) #check
        
        # roll [joint5]
        x_axes = joystick.axes[0]
        if (x_axes > 0.9 ): #clockwise
            print("roll colockwise")
            target_angle = joint_5 - 0.1
            target_joints = [joint_1, joint_2, joint_3, joint_4, target_angle]
            self.robot.arm.set_joint_positions(target_joints,plan=True)
        elif (x_axes < -0.9):
            print("roll anti-colockwise")
            target_angle = joint_5 + 0.1
            target_joints = [joint_1, joint_2, joint_3, joint_4, target_angle]
            self.robot.arm.set_joint_positions(target_joints,plan=True)
            
        # pitch [joint4]
        y_axes = joystick.axes[1]
        if (y_axes > 0.9 ): #anti-clockwise
            print("pitch up")
            target_angle = joint_4 - 0.1
            #print(target_angle)
            target_joints = [joint_1, joint_2, joint_3, target_angle, joint_5]
            self.robot.arm.set_joint_positions(target_joints,plan=True)
        elif (y_axes < -0.9):
            print("pitch down")
            target_angle = joint_4 + 0.1
            target_joints = [joint_1, joint_2, joint_3, target_angle, joint_5]
            self.robot.arm.set_joint_positions(target_joints,plan=True)
        #print(x_axes,y_axes)

    def jointstate_callback(self,joint_data):
        self.joint = JointState()
        self.joint = joint_data

	
	

if __name__ == '__main__':
    rospy.init_node('vrcontroller', anonymous=True)
    VRController = subvrcontrollerpub()
    rospy.spin()
