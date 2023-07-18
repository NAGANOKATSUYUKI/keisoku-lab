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
        self.bbox = BoundingBox()
        self.m_pub_threshold = rospy.get_param("~pub_threshold", 0.40)

        sub_cam_rgb      = rospy.Subscriber("/hsrb/head_rgbd_sensor/rgb/image_raw", Image, self.ImageCallback)
        sub_darknet_bbox = rospy.Subscriber("/darknet_ros/bounding_boxes", BoundingBoxes, self.DarknetBboxCallback)
        sub_cam_depth    = rospy.Subscriber("/hsrb/head_rgbd_sensor/depth_registered/image_raw", Image, self.DepthCallback) 

    def ImageCallback(self, cam_image_msg):
        try:
            # ROSのImageメッセージをOpenCVの画像形式に変換
            cam_image = self.cv_bridge.imgmsg_to_cv2(cam_image_msg, "bgr8")
            height, width = cam_image.shape[:2]
            
            if self.bbox.probability > 0.0 :

                #中心座標
                w = self.bbox.xmax - self.bbox.xmin
                h = self.bbox.ymax - self.bbox.ymin
                x = self.bbox.xmin + w/2
                y = self.bbox.ymin + h/2
                class_name = str(self.bbox.Class)
                 
                #深度距離
                depth_x = int((self.bbox.xmax + self.bbox.xmin) // 2)
                depth_y = int((self.bbox.ymax + self.bbox.ymin) // 2)
                bbox_depth = self.depth_image[depth_y][depth_x]

                rospy.loginfo("Class: %s, Score: %.2f, center: x=%.1f, y=%.1f, Dist: %dmm" % (class_name, self.bbox.probability, x, y, bbox_depth))
                # rospy.loginfo("color:width= %d, height= %d, depth:width= %d, height= %d" %(width, height, self.depth_width, self.depth_height ))

                #検出したものを円で囲む
                cv2.circle(cam_image, (int(x), int(y)), 5, (0,0,255), -1)

                #検出したものを矩形で囲む
                cv2.rectangle(cam_image, (self.bbox.xmin, self.bbox.ymin), (self.bbox.xmax, self.bbox.ymax),(0,0,255), 2)
                cv2.putText(cam_image, class_name, (self.bbox.xmin, self.bbox.ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255),2 )
                
                cv2.imshow("cam_image", cam_image)
                cv2.waitKey(1)
                cv2.imshow("depth_image", self.depth_image)
                cv2.waitKey(1)
            else :
                cv2.imshow("cam_image", cam_image)
                cv2.waitKey(1)
                cv2.imshow("depth_image", self.depth_image)
                cv2.waitKey(1)

        except CvBridgeError as e:
            rospy.logerr(e)
    
    def DepthCallback(self, depth_image_data):
        self.depth_image = None
        try:
            self.depth_image = self.cv_bridge.imgmsg_to_cv2(depth_image_data, "passthrough")
            self.depth_height, self.depth_width = self.depth_image.shape[:2]

        except CvBridgeError as e:
            rospy.logerr(e)

    def DarknetBboxCallback(self, darknet_bboxs):

        bboxs = darknet_bboxs.bounding_boxes
        bbox = BoundingBox()
        if len(bboxs) != 0 :
            for i, bb in enumerate(bboxs) :
                if bboxs[i].Class == 'bottle' and bboxs[i].probability >= self.m_pub_threshold:
                    bbox = bboxs[i]        
        self.bbox = bbox
    
if __name__ == '__main__':
    try:
        rospy.init_node('yolo_object_detection', anonymous=True)

        data = Detector()
        rospy.loginfo("data Initialized")
        rospy.spin()  

    except rospy.ROSInterruptException:
        pass
