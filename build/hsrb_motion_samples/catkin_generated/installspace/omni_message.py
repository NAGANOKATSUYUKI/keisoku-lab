#!/usr/bin/env python3
# Copyright (C) 2016 Toyota Motor Corporation
import controller_manager_msgs.srv
import rospy
import trajectory_msgs.msg

rospy.init_node('test')

# initialize ROS publisher
pub = rospy.Publisher(
    '/hsrb/omni_base_controller/command',
    trajectory_msgs.msg.JointTrajectory, queue_size=10)

# wait to establish connection between the controller
while pub.get_num_connections() == 0:
    rospy.sleep(0.1)

# make sure the controller is running
rospy.wait_for_service('/hsrb/controller_manager/list_controllers')
list_controllers = rospy.ServiceProxy(
    '/hsrb/controller_manager/list_controllers',
    controller_manager_msgs.srv.ListControllers)
running = False
while running is False:
    rospy.sleep(0.1)
    for c in list_controllers().controller:
        if c.name == 'omni_base_controller' and c.state == 'running':
            running = True

# fill ROS message
traj = trajectory_msgs.msg.JointTrajectory()
traj.joint_names = ["odom_x", "odom_y", "odom_t"]
p = trajectory_msgs.msg.JointTrajectoryPoint()
p.positions = [1, 1, 0]
p.velocities = [0, 0, 0]
p.time_from_start = rospy.Duration(15)
traj.points = [p]

# publish ROS message
pub.publish(traj)
