import cv2
import mediapipe as mp
import numpy as np
import time

# 설정
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 상태 상수
STATE_WAITING = 0      # 준비
STATE_CALIBRATING = 1  # 측정 중
STATE_MONITORING = 2   # 감시 중

# 변수 초기화
current_state = STATE_WAITING
calibration_frames = [] 
standard_pose = None    
threshold = 0.2

# 2. 카메라 연결
cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION) 
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)

print("🚀 FocusTrack V2.0 시작")
print("⌨️ 'c' 키를 누르면 캘리브레이션(기준 자세 측정)을 시작합니다.")

