#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from darknet_ros_msgs.msg import BoundingBoxes, BoundingBox
import cv2

class Detector():
    def __init__(self) :

        self.cv_bridge = CvBridge()
        self.person_bbox = BoundingBox()
        self.bbox = self.person_bbox


        self.m_pub_threshold = rospy.get_param("~pub_threshold", 0.40)

        sub_cam_rgb = rospy.Subscriber("/camera/color/image_raw", Image, self.ImageCallback)
        sub_darknet_bbox   =  rospy.Subscriber('/darknet_ros/bounding_boxes', BoundingBoxes, self.DarknetBboxCallback)

        return

    def ImageCallback(self, cam_image_msg):
        try:
            # ROSのImageメッセージをOpenCVの画像形式に変換
            cam_image = self.cv_bridge.imgmsg_to_cv2(cam_image_msg, "bgr8")
            cv2.namedWindow("cam_image")
            cv2.imshow("cam_image", cam_image)
            cv2.waitKey(10)
        except CvBridgeError as e:
            rospy.logerr(e)

        if self.bbox.probability > 0.0 :
            
            rospy.loginfo("class:person, Score: %.2f, center: %.3d " %(self.bbox.probability, self.bbox.xmax))
            # cv2.rectangle(cam_image, (self.bbox.xmin, self.bbox.ymin), (self.bbox.xmax, self.bbox.ymax),(0,0,255), 2) #画面上の検出したものを矩形を描画する
            # text_top = (self.bbox.xmin, self.bbox.ymin - 10)
            # text_bot = (self.bbox.xmin + 80, self.bbox.ymin +5)
            # text_pos = (self.bbox.xmin + 5, self.bbox.ymin)
            # text_pos = str(text_pos)
            # cv2.rectangle(cam_image, text_top, text_bot, (0,0,0), -1)
            
    def DarknetBboxCallback(self, darknet_bboxs):

        bboxs = darknet_bboxs.bounding_boxes
        bbox = BoundingBox()
        if len(bboxs) != 0 :
            for i, bb in enumerate(bboxs) :
                if bboxs[i].Class == 'person' and bboxs[i].probability >= self.m_pub_threshold:
                    bbox = bboxs[i]        
        self.bbox = bbox

    
if __name__ == '__main__':
    try:
        # ノードの初期化
        rospy.init_node('yolo_object_detection', anonymous=True)

        data = Detector()
        rospy.loginfo("data Initialized")
        rospy.spin()  # メッセージの受信と処理を継続
        

    except rospy.ROSInterruptException:
        pass
