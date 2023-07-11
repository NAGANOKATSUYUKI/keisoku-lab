#!/usr/bin/env python3

import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

def image_callback(msg):
    bridge = CvBridge()
    cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
    cv2.imshow("realsense_camera", cv_image)
    cv2.waitKey(1)

if __name__ == '__main__':
    rospy.init_node('usb_camera_display_node')
    rospy.Subscriber('/camera/color/image_raw', Image, image_callback)
    cv2.namedWindow("USB Camera", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("USB Camera", 640, 480)
    rospy.spin()