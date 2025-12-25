import cv2
import mediapipe as mp
import numpy as np
import time

# 설정
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

