#!/usr/bin/python3
# -*- coding: utf-8 -*-

import hsrb_interface
import rospy
import sys
from hsrb_interface import geometry
from geometry_msgs.msg import Point

# 把持力[N]
_GRASP_FORCE=0.6
# ボトルのtf名
_BOTTLE_TF='target_frame'
# グリッパのtf名
_HAND_TF='hand_palm_link'

# ロボット機能を使うための準備
robot = hsrb_interface.Robot()
omni_base = robot.get('omni_base')
whole_body = robot.get('whole_body')
gripper = robot.get('gripper')
tts = robot.get('default_tts')

# bottleのマーカの手前[m],z軸回に-1.57回転させた姿勢
bottle_to_hand = geometry.pose(z=-0.15, ek=-1.57)

# handを0.1[m]上に移動させる姿勢
hand_up = geometry.pose(x=0.1)

# handを0.2[m]手前に移動させる姿勢
hand_back = geometry.pose(z=-0.2)

camera_coords = [0.0,0.0,0.0]

def CoordinatePoint_callback(coordinate_msg):
        try:
            
            camera_coords[0] =  coordinate_msg.x
            camera_coords[1] =  coordinate_msg.y
            camera_coords[2] =  coordinate_msg.z

            rospy.loginfo("x= %0.2f, y= %0.2f, z=%0.2f", camera_coords[0],camera_coords[1], camera_coords[2])
        except :
            rospy.loginfo("Unable to create tf")


if __name__=='__main__':
    
    rospy.Subscriber("point_topic", Point, CoordinatePoint_callback)
    #一言
    rospy.sleep(3.0)
    tts.say('準備OK')
    rospy.sleep(3.0)

    rate = rospy.Rate(10)  # ループの周波数（10Hzを指定）
    while not rospy.is_shutdown():
        rate.sleep()
        if 1.5 > camera_coords[2] > 0.5:
                try:
                        gripper.command(0.0)
                        gripper.command(1.0)
                        # whole_body.move_to_neutral()
                except:
                        # tts.say('初期化失敗')
                        rospy.logerr('fail to init')

                try:
                        if 1.5 > camera_coords[2] > 0.5:
                                # 遷移後に手先を見るようにする
                                # whole_body.looking_hand_constraint = True
                                # ペットボトルの手前に手を持ってくる
                                whole_body.move_end_effector_pose(bottle_to_hand, _BOTTLE_TF)
                                whole_body.move_end_effector_pose(geometry.pose(z = 0.1), _HAND_TF)
                                # 力を指定して把持する
                                gripper.apply_force(_GRASP_FORCE, delicate = True)

                                rospy.sleep(2.0)
                                # 手先相対で上にハンドを移動
                                whole_body.move_end_effector_pose(hand_up, _HAND_TF)
                                # 手先相対で後ろにハンドを移動
                                whole_body.move_end_effector_pose(hand_back, _HAND_TF)
                                whole_body.move_to_neutral()
                                rospy.sleep(2.0)
                        
                                # 初期位置に移動
                                omni_base.go_abs(0.0, 0.0, 0.0, 300.0)
                                # 物体を右の箱に入れる想定
                                omni_base.go_rel(0.0, 0.0, -1.57, 100.0)#右向く
                                gripper.command(1.0)
                                omni_base.go_rel(0.0, 0.0, 1.57, 100.0)#左向く
                                whole_body.move_to_go()
                                # whole_body.move_to_joint_positions({"head_tilt_joint": -0.3})
                except:
                        # tts.say('把持失敗')
                        rospy.logerr('fail to grasp')
                        break  # ループを終了してプログラムを終了

                