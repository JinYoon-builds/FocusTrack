import mediapipe as mp
import cv2

class PoseWrapper:
    def __init__(self):
        self.mp_pose = mp.solutions.pose

        self.pose = self.mp_pose.Pose(
            min_detection_confidence = 0.5,
            min_tracking_confidence=0.5
        )

    def process(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.pose.process(rgb_frame)