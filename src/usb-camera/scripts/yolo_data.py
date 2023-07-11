#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from darknet_ros_msgs.msg import BoundingBoxes, BoundingBox
import cv2


def image_callback(msg):
    try:
        bridge = CvBridge()
        # ROSのImageメッセージをOpenCVの画像形式に変換
        cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
        
        # 画像処理や物体検出のための処理を追加
        
        # 検出結果を表示
        cv2.imshow("YOLO Object Detection", cv_image)
        cv2.waitKey(1)
        
    except Exception as e:
        print(e)

def main():
    # ノードの初期化
    rospy.init_node('yolo_object_detection')
    
    # Imageトピックのサブスクライバを作成
    image_subscriber = rospy.Subscriber('/camera/color/image_raw', Image, image_callback)
    
    # メッセージの受信と処理を継続
    rospy.spin()

if __name__ == '__main__':
    main()
