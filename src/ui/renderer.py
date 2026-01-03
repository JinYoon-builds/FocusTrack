import cv2
import mediapipe as mp

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (0, 255, 255)

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
    def _draw_text(self, frame, text, pos, color, scale = 1.0):
        cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # 상황별 화면 
    # 1. 대기 화면
    def draw_waiting(self, frame, info_text = ""):
        center_x = frame.shape[1] // 2
        self._draw_text(frame, "Press 'c' to Calibrate", (center_x - 200, 100), RED, 1.2)

        if info_text:
            self._draw_text(frame, info_text, (center_x - 200, 300), GREEN, 1.0)
    
    # 2. 캘리브레이션 화면: int count, total 필요, str 상태메시지 필요
    def draw_calibration(self, frame, message: str, count: int, target:int):
        center_x = frame.shape[1] // 2
        
        # 안내 문구 출력
        self._draw_text(frame, message, (center_x - 200, 100), YELLOW, 1.0)

        # 진행상황 출력
        status = f"Progress: {count} / {target}"
        self._draw_text(frame, status, (center_x - 150, 200), BLUE, 0.8)
        

    # 3. 감시 화면: str status, float dist 필요
    def draw_monitoring(self, frame, status : str, dist : float):
        center_x = frame.shape[1] // 2
        if status == "FOCUSED":
            color = GREEN
        else:
            color = BLUE
        self._draw_text(frame, f"{status} (Diff: {dist: .3f})", (center_x - 200, 300), color, 1.0)
        
