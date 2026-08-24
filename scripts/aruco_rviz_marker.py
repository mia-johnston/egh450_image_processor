#!/usr/bin/env python3

import re
import rospy

from std_msgs.msg import String
from visualization_msgs.msg import Marker


POSE_TOPIC = "/aruco/pose_log"
MARKER_TOPIC = "/aruco/rviz_marker"


class ArucoRvizMarker:

    def __init__(self):

        self.marker_pub = rospy.Publisher(
            MARKER_TOPIC,
            Marker,
            queue_size=10
        )

        self.pose_sub = rospy.Subscriber(
            POSE_TOPIC,
            String,
            self.pose_callback
        )

        rospy.loginfo("ArUco RViz marker node started")
        rospy.loginfo("Listening to {}".format(POSE_TOPIC))
        rospy.loginfo("Publishing to {}".format(MARKER_TOPIC))


    def pose_callback(self, msg):

        # Expected text format:
        # ID 32: pixel=(205, 190), x=2.10, y=1.35, z=1.20, dist=2.80m

        matches = re.findall(
            r"ID\s+(\d+):.*?"
            r"x=([-\d.]+),\s*"
            r"y=([-\d.]+),\s*"
            r"z=([-\d.]+),\s*"
            r"dist=([-\d.]+)m",
            msg.data
        )

        for match in matches:

            marker_id = int(match[0])
            x = float(match[1])
            y = float(match[2])
            z = float(match[3])
            distance = float(match[4])

            self.publish_marker(
                marker_id,
                x,
                y,
                z,
                distance
            )


    def publish_marker(self, marker_id, x, y, z, distance):

        marker = Marker()

        # Coordinates in pose_log are assumed to now be
        # relative to the ROS map frame
        marker.header.frame_id = "map"
        marker.header.stamp = rospy.Time.now()

        marker.ns = "aruco_detection"
        marker.id = marker_id

        marker.type = Marker.CUBE
        marker.action = Marker.ADD

        # Use the actual ArUco position from pose_log
        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.pose.position.z = z

        marker.pose.orientation.x = 0.0
        marker.pose.orientation.y = 0.0
        marker.pose.orientation.z = 0.0
        marker.pose.orientation.w = 1.0

        # Visual size in RViz
        marker.scale.x = 0.25
        marker.scale.y = 0.25
        marker.scale.z = 0.25

        # Green marker
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        marker.color.a = 1.0

        # Marker disappears if detections stop
        marker.lifetime = rospy.Duration(1.0)

        self.marker_pub.publish(marker)

        rospy.loginfo_throttle(
            1.0,
            "ArUco ID {} at map position x={:.2f}, y={:.2f}, z={:.2f}".format(
                marker_id,
                x,
                y,
                z
            )
        )


if __name__ == "__main__":

    rospy.init_node("aruco_rviz_marker")

    ArucoRvizMarker()

    rospy.spin()