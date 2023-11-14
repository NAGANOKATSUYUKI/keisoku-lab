#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ImageProcessorNode:
    def __init__(self):
        rospy.init_node('image_processor_node')

        # 画像を受け取るトピックと出力するトピックを指定
        self.image_topic = "/hsrb/hand_camera/image_raw"
        self.rotated_image_topic = "/hsrb/hand_rotation/image_raw"

        # メッセージの変換に使用するCvBridgeのインスタンスを作成
        self.bridge = CvBridge()

        # 画像を回転させた後、新しいトピックに出力するパブリッシャーを作成
        self.pub = rospy.Publisher(self.rotated_image_topic, Image, queue_size=10)

        # 画像を受け取るサブスクライバーを設定
        rospy.Subscriber(self.image_topic, Image, self.image_callback)

    def image_callback(self, msg):
        # 画像メッセージをOpenCV形式に変換
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="rgb8")

        # 画像を回転させる
        rotated_image = cv2.rotate(cv_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # 回転させた画像を新しいトピックに出力
        rotated_msg = self.bridge.cv2_to_imgmsg(rotated_image, encoding="rgb8")
        self.pub.publish(rotated_msg)

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    node = ImageProcessorNode()
    node.run()
