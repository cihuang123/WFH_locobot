#!/usr/bin/env python

import argparse
import copy
import signal
import sys
import time

import numpy as np
import rospy
from geometry_msgs.msg import Quaternion, PointStamped
from pyrobot import Robot
from tf import TransformListener

from grasp_samplers.grasp_model import GraspModel

MODEL_URL = "https://www.dropbox.com/s/fta8zebyzfrt3fw/checkpoint.pth.20?dl=0"
BB_SIZE = 5
MAX_DEPTH = 3.0
BASE_FRAME = "base_link"
KINECT_FRAME = "camera_color_optical_frame"
DEFAULT_PITCH = 1.57
MIN_DEPTH = 0.1
N_SAMPLES = 100
PATCH_SIZE = 100

from IPython import embed
from pyrobot.utils.util import try_cv2_import

cv2 = try_cv2_import()

# DEFAULT_PITCH_EPSILON = 0.02

from locobot import Grasper # Inherit class "Grasper" from locobot.py

class Grasper_Depth(Grasper):
    def __init__(
        self,
        url=MODEL_URL,
        model_name="model.pth",
        n_samples=N_SAMPLES,
        patch_size=PATCH_SIZE,
        *kargs,
        **kwargs
    ):
        """ 
        The constructor for :class:`Grasper` class. 

        :param url: Link to the grasp model file
        :param model_name: Name of the path where the grasp model will be saved
        :param n_samples: Number of samples for the grasp sampler
        :param patch_size: Size of the patch for the grasp sampler
        :type url: string
        :type model_name: string
        :type n_samples: int
        :type patch_size: int
        """

        # TODO - use planning_mode=no_plan, its better
        self.robot = Robot(
            "locobot_kobuki",
            arm_config={"use_moveit": True, "moveit_planner": "ESTkConfigDefault"},
        )
        self.grasp_model = GraspModel(
            model_name=model_name, url=url, nsamples=n_samples, patchsize=patch_size
        )
        self.pregrasp_height = 0.24
        self.grasp_height = 0.15
        self.default_Q = Quaternion(0.0, 0.0, 0.0, 1.0)
        self.grasp_Q = Quaternion(0.0, 0.707, 0.0, 0.707)
        self.retract_position_1 = list([1.5, 0.5, 0.3, -0.7, 0.0])
        self.retract_position_2 = list([1.7, 0.9, 0.3, -1.1, 0.0])
        self.reset_pan = 0.0
        self.reset_tilt = 0.8
        self.n_tries = 5
        self._sleep_time = 2
        self._transform_listener = TransformListener()

    def reset(self):
        """ 
        Resets the arm to it's retract position.

        :returns: Success of the reset procedure
        :rtype: bool
        """
        success = True
        for _ in range(self.n_tries):
            self.robot.arm.go_home()
            self.robot.arm.set_joint_positions(self.retract_position_1, plan=False)
            self.robot.arm.set_joint_positions(self.retract_position_2, plan=False)
            if success == True:
                break
        self.robot.gripper.open()
        self.robot.camera.set_pan(self.reset_pan)
        self.robot.camera.set_tilt(self.reset_tilt)
        return success

    def _process_depth(self, cur_depth=None):
        if cur_depth is None:
            cur_depth = self.robot.camera.get_depth()
            print ("depth1")
        cur_depth = cur_depth * 1000.0  # conversion from mm to m
        print ("depth2")
        cur_depth[cur_depth > MAX_DEPTH] = 0.0
        print ("depth3")
        return cur_depth
    
    def compute_grasp(self, dims=[(150, 480), (0, 640)], display_grasp=False):
        """ 
        Runs the grasp model to generate the best predicted grasp.
        
        :param dims: List of tuples of min and max indices of the image axis.
        :param display_grasp: Displays image of the grasp.
        :type dims: list
        :type display_grasp: bool

        :returns: Grasp configuration
        :rtype: list
        """

        img = self.robot.camera.get_rgb()
        img = img[dims[0][0] : dims[0][1], dims[1][0] : dims[1][1]]
        # selected_grasp = [183, 221, -1.5707963267948966, 1.0422693]
        selected_grasp = list(self.grasp_model.predict(img))
        rospy.loginfo("Pixel grasp: {}".format(selected_grasp))
        img_grasp = copy.deepcopy(selected_grasp)
        selected_grasp[0] += dims[0][0]
        selected_grasp[1] += dims[1][0]
        selected_grasp[:2] = self.get_3D(selected_grasp[:2])[:2]
        selected_grasp[2] = selected_grasp[2]
        if display_grasp:
            self.grasp_model.display_predicted_image()
            # im_name = '{}.png'.format(time.time())
            # cv2.imwrite('~/Desktop/grasp_images/{}'.format(im_name), self.grasp_model._disp_I)
        return selected_grasp

def main(args):
    """
    This is the main function for running the grasping demo.
    """

    grasper = Grasper_Depth(n_samples=args.n_samples, patch_size=args.patch_size)
    signal.signal(signal.SIGINT, grasper.signal_handler)
    for i in range(args.n_grasps):
        rospy.loginfo("Grasp attempt #{}".format(i + 1))
        success = grasper.reset()
        if not success:
            rospy.logerr("Arm reset failed")
            continue
        grasp_pose = grasper.compute_grasp(display_grasp=args.no_visualize)
        print("\n\n Grasp Pose: \n\n {} \n\n".format(grasp_pose))
        grasper.grasp(grasp_pose)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process args for grasper")
    parser.add_argument(
        "--n_grasps", help="Number of grasps for inference", type=int, default=5
    )
    parser.add_argument(
        "--n_samples",
        help="Number of samples for a single grasp inference",
        type=int,
        default=N_SAMPLES,
    )
    parser.add_argument(
        "--patch_size",
        help="Size of a sampled grasp patch",
        type=int,
        default=PATCH_SIZE,
    )
    parser.add_argument(
        "--no_visualize",
        help="False to visualize grasp at each iteration, True otherwise",
        dest="display_grasp",
        action="store_false",
    )
    parser.set_defaults(no_visualize=True)

    args = parser.parse_args()

    main(args)