#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from darknet_ros_msgs.msg import BoundingBoxes, BoundingBox
from cv_bridge import CvBridge, CvBridgeError

class Detector():
    def __init__(self):
        rospy.init_node("Point_hand_topic")
        self.cv_bridge = CvBridge()
        self.bbox = BoundingBox()
        self.m_pub_threshold = rospy.get_param("~pub_threshold", 0.30)

        self.cam_x = 0.0
        self.cam_y = 0.0
        self.switch = False

        sub_darknet_bbox  = rospy.Subscriber("/darknet_ros1/bounding_boxes", BoundingBoxes, self.DarknetBboxCallback)

    #検出
    def DarknetBboxCallback(self, darknet_bboxs):
        bboxs = darknet_bboxs.bounding_boxes
        bbox = BoundingBox()
        if len(bboxs) != 0 :
            for i, bb in enumerate(bboxs) :
                if bboxs[i].Class == 'bottle' and bboxs[i].probability >= self.m_pub_threshold:
                    bbox = bboxs[i]   
                    self.bbox = bbox

                    #中心座標
                    self.cam_x = self.bbox.xmin + (self.bbox.xmax - self.bbox.xmin) / 2
                    self.cam_y = self.bbox.ymin + (self.bbox.ymax - self.bbox.ymin) / 2
                    self.switch = True
                    self.CameraInfo_callback()
                    self.switch = False
                else:
                    self.cam_x = 0
                    self.cam_y = 0

    #topic_publish
    def CameraInfo_callback(self):
        if self.cam_x != 0.0 and self.cam_y != 0.0 or self.cam_x > self.cam_y :
            try:
                if self.cam_y > 500 :
                    if self.switch :
                            pub = rospy.Publisher("point_hand_topic", Point, queue_size=10)
                            point_msg = Point()
                            point_msg.x = self.cam_x
                            point_msg.y = self.cam_y
                            point_msg.z = 0.0
                            point_msg.z = int(self.switch)
                            pub.publish(point_msg)
                            rospy.loginfo("x=%.1f y=%.1f switch --> True", self.cam_x, self.cam_y)
                    else:
                        rospy.logwarn("switch --> False")
                else:
                    rospy.logwarn("Out of range")
            except:
                rospy.logwarn("Publish_ERROR")
        else:
            rospy.logwarn("Not Detection")

if __name__=="__main__":
    rospy.loginfo("Unable to create tf")
    try:
        Detector()
        rospy.spin()

    except rospy.ROSInterruptException:
        pass

#1117