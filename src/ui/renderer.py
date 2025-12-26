import cv2
import mediapipe as mp

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Renderer:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose

    # 뼈대 그리기
    def draw_skeleton(self, frame, landmarks):
        if landmarks:
            self.mp_drawing.draw_landmarks(
                frame, landmarks, self.mp_pose.POSE_CONNECTIONS
            )

    # 내부 헬퍼 함수
    def _draw_text(self, frame, text, color = RED):
        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # 상황별 화면 
    # 1. 대기 화면
    def draw_waiting(self, frame):
        self._draw_text(frame, "Press 'c' to Calibrate", RED)
    
    # 2. 캘리브레이션 화면: int count 필요
    def draw_calibration(self, frame, count: int):
        self._draw_text(frame, f"Collecting data ... {count} / 30", BLUE)

    # 3. 감시 화면: str status, float dist 필요
    def draw_monitoring(self, frame, status : str, dist : float):
        if status == "FOCUSED":
            color = GREEN
        else:
            color = BLUE
        self._draw_text(frame, f"{status} (Diff: {dist: .3f})", color)
        
