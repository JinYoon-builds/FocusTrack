import numpy as np

def get_nose_vector(landmarks):
    nose = landmarks.landmark[0]
    return np.array([nose.x, nose.y])

# 캘리브레이터
class PoseCalibrator:
    def __init__(self, buffer_size = 30):
        self.buffer_size = buffer_size
        self.buffer = [] # 데이터 담기

    def add_data(self, landmarks):
        # 프레임마다 자세 데이터 수집   
        vector = get_nose_vector(landmarks)
        self.buffer.append(vector)
        return len(self.buffer)

    def is_ready(self):
        return len(self.buffer) >= self.buffer_size
    
    def get_standard_pose(self):
        # 평균을 계산해서 기준 자세 반환
        if not self.buffer:
            return None
        
        standard_pose = np.mean(self.buffer, axis=0)
        self.buffer = [] # 초기화
        return standard_pose
    
# 판정기
class FocusAnalyzer:
    def __init__(self, threshold = 0.2):
        self.threshold = threshold
        self.standard_pose = None

    def set_standard_pose(self, pose_vector):
        self.standard_pose = pose_vector
        print(f"기준 자세 : {self.standard_pose}")

    def analyze(self, landmarks):
        # 실시간 감시 및 판정
        if self.standard_pose is None:
            return "UNKNOWN", 0.0
        
        current_vector = get_nose_vector(landmarks)

        dist = np.linalg.norm(current_vector - self.standard_pose)

        if dist < self.threshold:
            return "Focused", dist
        
        else:
            return "Distracted", dist