# 미디어파이프와 캠 테스트: 코 위치 찍어보기

import cv2
import mediapipe as mp
import time

# 미디어파이프 설정
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

mp_drawing = mp.solutions.drawing_utils

# 카메라 설정
cap = cv2.VideoCapture(0,cv2.CAP_AVFOUNDATION)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"📸 현재 해상도: {w} x {h}")

if not cap.isOpened():
    print("❌ 카메라를 열 수 없습니다!")
    exit()

print("✅ 준비 완료! 카메라 작동...")


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 추론
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )
        nose = results.pose_landmarks.landmark[0]
        print(f"코 위치: {nose.x}, {nose.y}")

    else: 
        print("사람 찾는 중...")

    # 화면 보여주기, q 누르면 종료
    cv2.imshow('Mediapipe Test', frame)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
