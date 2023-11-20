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




if __name__=='__main__':
    
    while True:
        
        if hand ==trueのとき:
            
            後ろに下がる
            ニュートラル
            顔をさげる
            
        else:
            通常の取りに行く*うごき
