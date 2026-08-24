#!/usr/bin/env python3

import rospy
import re
import subprocess
from std_msgs.msg import String

# Keeps track of markers already announced
spoken_markers = set()


def pose_log_callback(msg):
    global spoken_markers

    # Example received text:
    # ID 3: pixel=(...), x=..., y=..., z=..., dist=...

    marker_ids = re.findall(r"ID\s+(\d+):", msg.data)

    for marker_id in marker_ids:

        # Only speak the first time this marker is detected
        if marker_id not in spoken_markers:

            text = "Target detected"

            rospy.loginfo(
                "ArUco marker %s detected - speaking warning",
                marker_id
            )

            # Run eSpeak command
            subprocess.Popen(["espeak", text])

            # Remember this marker so it isn't announced repeatedly
            spoken_markers.add(marker_id)


if __name__ == "__main__":

    rospy.init_node("aruco_speech")

    rospy.Subscriber(
        "/aruco/pose_log",
        String,
        pose_log_callback
    )

    rospy.loginfo("ArUco speech node running")
    rospy.loginfo("Listening to /aruco/pose_log")

    try:
        rospy.spin()

    except rospy.ROSInterruptException:
        pass