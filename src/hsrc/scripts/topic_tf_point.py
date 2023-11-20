#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Point
from sensor_msgs.msg import Image, CameraInfo
from darknet_ros_msgs.msg import BoundingBoxes, BoundingBox
from cv_bridge import CvBridge, CvBridgeError
import tf2_ros
import tf2_geometry_msgs
from geometry_msgs.msg import TransformStamped

class Tfpoint_Detector:
    def __init__(self):
        self.bbox = BoundingBox()
        self.pub_threshold = rospy.get_param("~pub_threshold", 0.40)
        self.pub = rospy.Publisher("point_topic", Point, queue_size=10)

        # average variables
        self.i = 0
        self.sum_x = 0
        self.sum_y = 0
        self.sum_z = 0
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.frame_count = 0

        # detection subscription
        self.sub_head_bbox = rospy.Subscriber("/darknet_ros0/bounding_boxes", BoundingBoxes, self.HeadBboxCallback)

    def HandBboxCallback(self, darknet_bboxs):
        bbox = BoundingBox()
        hand_bboxs = darknet_bboxs.bounding_boxes
        if hand_bboxs:
            for i in range(len(hand_bboxs)):
                if hand_bboxs[i].Class == "bottle" and hand_bboxs[i].probability >= self.pub_threshold:
                    bbox = hand_bboxs[i]
                    self.class_name = bbox.Class
                else:
                    pass
        else:
            pass

        hand_cam_x = bbox.xmin + (bbox.xmax - bbox.xmin) / 2
        hand_cam_y = bbox.ymin + (bbox.ymax - bbox.ymin) / 2
        rospy.loginfo("x = %.2f, y = %.2f", hand_cam_x, hand_cam_y)
        hand_cam_x = 0
        hand_cam_y = 0

    def HeadBboxCallback(self, darknet_bboxs):
        bbox = BoundingBox()
        head_bboxs = darknet_bboxs.bounding_boxes
        if head_bboxs:
            for i in range(len(head_bboxs)):
                if head_bboxs[i].Class == "bottle" and head_bboxs[i].probability >= self.pub_threshold:
                    bbox = head_bboxs[i]
                    self.class_name = bbox.Class
                else:
                    pass
        else:
            pass

        self.cam_x = bbox.xmin + (bbox.xmax - bbox.xmin) / 2
        self.cam_y = bbox.ymin + (bbox.ymax - bbox.ymin) / 2
        self.sub_head_swich = True
        self.sub_cam_depth = rospy.Subscriber("/hsrb/head_rgbd_sensor/depth_registered/image_raw", Image, self.DepthCallback)
        
        self.frame_count += 1
        if self.frame_count == 30:
            self.frame_count = 0
            self.sub_hand_bbox = rospy.Subscriber("/darknet_ros1/bounding_boxes", BoundingBoxes, self.HandBboxCallback)
        else:
            pass

    def DepthCallback(self, depth_image_data):
        try:
            if self.sub_head_swich:
                cv_bridge = CvBridge()
                cv_ptr = cv_bridge.imgmsg_to_cv2(depth_image_data, desired_encoding="32FC1")
                depth_x = int(self.cam_x)
                depth_y = int(self.cam_y)
                bbox_depth = cv_ptr[depth_y, depth_x]
                self.sub_camera_info = rospy.Subscriber("/hsrb/head_rgbd_sensor/depth_registered/camera_info", CameraInfo, self.CameraInfoCallback)
                self.sub_head_swich = False
            else:
                self.sub_cam_depth.unregister()
                self.sub_camera_info.unregister()
        except CvBridgeError as e:
            rospy.logerr("CvBridge Error: %s", e)

    def CameraInfoCallback(self, info_msg):
        if self.cam_x != 0.0 and self.cam_y != 0.0 or self.cam_x > self.cam_y:
            try:
                crrection_x = self.cam_x - info_msg.K[2]  # 320
                crrection_y = self.cam_y - info_msg.K[5]  # 280
                z = self.bbox_depth
                x1 = z * (crrection_x / info_msg.K[0])
                y1 = z * (crrection_y / info_msg.K[4])
                x = x1 * 0.001
                y = y1 * 0.001 + 0.2 * y1 * 0.001
                z = z * 0.001
            except Exception as e:
                rospy.logwarn("Transform Error: %s", str(e))

            if 0.40 < z <= 1.5 and -0.4 < x < 0.4:
                self.CoordinatePointCallback()
                self.sum_x += x
                self.sum_y += y
                self.sum_z += z
                self.i += 1
                rospy.loginfo("class:%s x = %.2f y = %.2f z = %.2f %d", self.class_name, x, y, z, self.i)
            else:
                rospy.logwarn("Out of range")

            if self.i == 30:
                x = self.sum_x / 30
                y = self.sum_y / 30
                z = self.sum_z / 30
                self.sum_x = 0
                self.sum_y = 0
                self.sum_z = 0
                point_msg = Point(x=x, y=y, z=z)
                self.pub.publish(point_msg)
                self.i = 0
            else:
                pass
        else:
            rospy.logwarn("Not Detection")

    def CoordinatePointCallback(self):
        try:
            static_tf_broadcaster = tf2_ros.TransformBroadcaster()

            gt = TransformStamped()
            gt.header.stamp = rospy.Time.now()
            gt.header.frame_id = "head_rgbd_sensor_link"
            gt.child_frame_id = "target_frame"
            gt.transform.translation.x = self.x
            gt.transform.translation.y = self.y
            gt.transform.translation.z = self.z

            q = tf2_geometry_msgs.transformations.quaternion_from_euler(0, 0, 0)
            gt.transform.rotation.x = q[0]
            gt.transform.rotation.y = q[1]
            gt.transform.rotation.z = q[2]
            gt.transform.rotation.w = q[3]

            static_tf_broadcaster.sendTransform(gt)
        except Exception as e:
            rospy.logerr("Unable to create tf: %s", str(e))

if __name__ == '__main__':
    rospy.init_node("Tfpoint_detector_node")
    tfpoint_detector = Tfpoint_Detector()
    rospy.spin()

#微妙