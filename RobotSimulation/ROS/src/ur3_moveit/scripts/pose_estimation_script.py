#!/usr/bin/env python3

from ur3_moveit.setup_and_run_model import *

import sys

import rospy
import io
import os
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# from get_balls_pos import PosEstimation
# from get_balls_pos_v2 import PosEstimation
from get_balls_pos_v3 import PosEstimation
from PlanningCore import get_strike_angles
from ur3_moveit.srv import PoseEstimationService, PoseEstimationServiceResponse
from PIL import Image, ImageOps
from geometry_msgs.msg import Point, Quaternion, Pose
from scipy.spatial.transform import Rotation as R

NODE_NAME = "PoseEstimationNode"
PACKAGE_LOCATION = os.path.dirname(os.path.realpath(__file__))[
    :-(len("/scripts"))]  # remove "/scripts"

count = 0

# MYNOTE: This is where the Pose Estimate operations is


def _save_image(req):
    """  convert raw image data to a png and save it
    Args:
        req (PoseEstimationService msg): service request that contains the image data
     Returns:
        image_path (str): location of saved png file
    """
    global count
    count += 1

    image_height = req.image.width
    image_width = req.image.height
    image = Image.frombytes(
        'RGBA', (image_width, image_height), req.image.data)
    image = ImageOps.flip(image)
    image_name = "Input" + str(count) + ".png"
    if not os.path.exists(PACKAGE_LOCATION + "/images/"):
        os.makedirs(PACKAGE_LOCATION + "/images/")
    image_path = PACKAGE_LOCATION + "/images/" + image_name
    image.save(image_path)
    return image_path


def _run_model(image_path, req):
    """ run the model and return the estimated posiiton/quaternion
    Args:
        image_path (str): location of saved png file
     Returns:
        position (float[]): object estmated x,y,z
        quaternion (float[]): object estimated w,x,y,z
    """
    # output = run_model_main(image_path, MODEL_PATH)
    # position = output[1].flatten()
    # quaternion = output[0].flatten()
    # print('=====> todo: running model, to get estimated pose')
    # print("cue ball pose")
    # print(req.cue_ball_pose)
    # print("other balls")
    # print(req.balls_pose)



    debug = False
    p1 = 105
    p2 = 16
    white_crit = 1.8
    estimator = PosEstimation(image_path)
    cue_ball_center, balls_center = estimator.getAllBalls(debug, p1, p2, white_crit)
    # cue_ball_center, balls_center = estimator.getAllBalls(debug)
    if cue_ball_center is None or len(cue_ball_center) == 0:
        cue_ball_center = [[0, 0]]
    # balls_center = estimator.getBallsPosition(w, h, debug, cue_x = cue_ball_center[0], cue_y = cue_ball_center[1])
    print('cue ball center: =========>')
    print(cue_ball_center[0])
    print('balls center: =========>')
    print(balls_center)


    # TODO: planning algorithm
    # table = init_table(cueballpos=cue_ball_center[0], ballposlist=balls_center)
    # angles = search_optimal_strike(table=table, dt=0.02, dang=0.5)
    import time
    t1 = time.time()
    angles = get_strike_angles(
        cue_ball_pos=cue_ball_center[0],
        balls_pos=balls_center,
        v_cue=1,
        dang=1,
        return_once_find=True,
        event_based=True,
        direct_strike=req.is_direct,
    )
    t2 = time.time()
    print('time: =========>')
    print(t2 - t1)
    print('angles: =========>')
    # angles = [(0, 78.13010235415602, (-0.3352243920078475, 2.5798335100894003))]
    print(angles)
    print(req.is_direct)

    if req.is_direct:
        position = [angles[0][2][0], 0, -angles[0][2][1]]
    else:
        position = [cue_ball_center[0][0], 0, -cue_ball_center[0][1]]
    
    quaternion = [angles[0][1], 0, 0, 0]

    
    return position, quaternion


def _format_response(est_position, est_rotation):
    """ format the computed estimated position/rotation as a service response
       Args:
           est_position (float[]): object estmated x,y,z
           est_rotation (float[]): object estimated Euler angles
        Returns:
           response (PoseEstimationServiceResponse): service response object
       """
    position = Point()
    position.x = est_position[0]
    position.y = est_position[1]
    position.z = est_position[2]

    rotation = Quaternion()
    rotation.x = est_rotation[0]
    rotation.y = est_rotation[1]
    rotation.z = est_rotation[2]
    rotation.w = est_rotation[3]

    pose = Pose()
    pose.position = position
    pose.orientation = rotation

    response = PoseEstimationServiceResponse()
    response.estimated_pose = pose
    return response


def pose_estimation_main(req):
    """  main callback for pose est. service.
    Args:
        req (PoseEstimationService msg): service request that contains the image data
     Returns:
       response (PoseEstimationServiceResponse): service response object
    """
    print("Started estimation pipeline")
    image_path = _save_image(req)
    print("Predicting from screenshot " + image_path)

    # This is the final pose, to guide the robot how to move
    # the core logic is in _run_model
    # mainly two things:
    # 1. get the balls and cue ball position
    # 2. decision
    # the output should be two list
    # est_position = [], length 3
    # est_rotation = [], length 4
    est_position, est_rotation = _run_model(image_path, req)
    response = _format_response(est_position, est_rotation)
    print("Finished estimation pipeline\n")
    return response


def main():
    """
     The function to run the pose estimation service
     """
    rospy.init_node(NODE_NAME)
    s = rospy.Service('pose_estimation_service',
                      PoseEstimationService, pose_estimation_main)
    print("Ready to estimate pose!")
    rospy.spin()


if __name__ == "__main__":
    main()
