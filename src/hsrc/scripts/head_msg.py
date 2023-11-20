#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from darknet_ros_msgs.msg import BoundingBoxes, BoundingBox
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import CameraInfo

class Detector():
    def __init__(self):
        rospy.init_node("Point_head_topic")
        self.cv_bridge = CvBridge()
        self.bbox = BoundingBox()
        self.m_pub_threshold = rospy.get_param("~pub_threshold", 0.20)

        self.cam_x = 0.0
        self.cam_y = 0.0

        sub_cam_depth     = rospy.Subscriber("/hsrb/head_rgbd_sensor/depth_registered/image_raw", Image, self.DepthCallback)
        sub_cam_info      = rospy.Subscriber("/hsrb/head_rgbd_sensor/depth_registered/camera_info", CameraInfo, self.CameraInfo_callback)
        sub_darknet_bbox  = rospy.Subscriber("/darknet_ros0/bounding_boxes", BoundingBoxes, self.DarknetBboxCallback)

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

    def DepthCallback(self, depth_image_data):
        try:
            #depth距離測定
            self.depth_image = self.cv_bridge.imgmsg_to_cv2(depth_image_data, "passthrough")
            depth_x = int(self.cam_x)
            depth_y = int(self.cam_y)
            self.bbox_depth = self.depth_image[depth_y][depth_x]

        except CvBridgeError as e:
            rospy.logerr("Cvbridge error: %s", e)

    #座標変換
    def CameraInfo_callback(self, info_msg):

        if self.cam_x != 0.0 and self.cam_y != 0.0 or self.cam_x > self.cam_y :
            try:
                self.x = self.cam_x - info_msg.K[2]
                self.y = self.cam_y - info_msg.K[5]
                self.z = self.bbox_depth

                self.x1 = self.z * self.x / info_msg.K[0]
                self.y1 = self.z * self.y / info_msg.K[4]

                self.x1 = self.x1 * 0.001
                self.y1 = self.y1 * 0.001 + 0.2 * self.y1 *0.001
                self.z = self.z * 0.001
            except:
                rospy.logwarn("transform_ERROR")

            #topic_publish
            try:
                if 0.40 < self.z < 1.4 or self.cam_x != 0.0 and self.cam_y != 0.0:
                    if -0.4 < self.x1 < 0.4 :
                        pub = rospy.Publisher("point_head_topic", Point, queue_size=10)
                        point_msg = Point()
                        point_msg.x = self.x1
                        point_msg.y = self.y1
                        point_msg.z = self.z
                        pub.publish(point_msg)
                        rospy.loginfo("x =%.2f y=%.2f z=%.2f ", self.x1, self.y1, self.z)
                    else:
                        rospy.logwarn("Out of range")
                else:
                    rospy.loginfo("x =%.2f y=%.2f z=%.2f Distance over", self.x1, self.y1, self.z)
                    self.cam_x = 0.0
                    self.cam_y = 0.0
                    # rospy.logwarn("Distance over")    
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
#1120