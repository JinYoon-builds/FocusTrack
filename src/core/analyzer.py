import numpy as np
from numpy.linalg import inv, LinAlgError

def extract_features(landmarks):
    # 양 어깨 중점을 (0, 0)으로 지정 센터링
    # 양 어깨 너비를 1.0으로 정규화 스케일링
    lm = landmarks.landmark

    points = np.array([ [p.x, p.y] for p in lm])

    # 필요 인덱스: 코, 왼눈, 오른눈, 왼귀, 오른귀, 왼어깨, 오른어깨
    indices = [0, 2, 5, 7, 8, 11, 12]
    selected_points = points[indices]

    # 센터링
    left_shoulder = points[11]
    right_shoulder = points[12]

    center = (left_shoulder + right_shoulder) / 2

    centered_points = selected_points - center

    # 스케일링: 크기 보정
    shoulder_width = np.linalg.norm(left_shoulder - right_shoulder)

    # 너비가 너무 작으면 1.0으로
    if shoulder_width < 1e-6:
        shoulder_width = 1.0
    
    normalized_points = centered_points / shoulder_width

    return normalized_points.flatten()


# 캘리브레이터
class PoseCalibrator:
    def __init__(self, buffer_size = 150):
        self.buffer_size = buffer_size
        self.buffer = [] # 데이터 담기

    def add_data(self, landmarks):
        # 프레임마다 자세 데이터 수집   
        vector = extract_features(landmarks)
        self.buffer.append(vector)
        return len(self.buffer)

    def is_ready(self):
        return len(self.buffer) >= self.buffer_size
    
    def get_statistics(self):
        # 평균벡터와 공분산 역행렬 반환 
        if not self.buffer: return None, None

        data = np.array(self.buffer)

        # 평균벡터
        mean_vector = np.mean(data, axis=0)

        # 공분산 행렬
        cov_matrix = np.cov(data, rowvar=False)

        # [★ 핵심 수정] "최소 분산 주입 (Regularization)"
        # 1e-2 (0.01) 정도로 키워서 "최소한의 숨쉬기"를 강제로 가정합니다.
        min_variance = 1e-2
        cov_matrix += np.eye(cov_matrix.shape[0]) * min_variance

        # 공분산의 역행렬
        try:
            inv_cov_matrix = inv(cov_matrix)
        except LinAlgError:
            # Singular Matrix라 역행렬이 안 구해지면 그냥 단위행렬로
            inv_cov_matrix = np.eye(len(mean_vector))

        return mean_vector, inv_cov_matrix

    
# 판정기
class FocusAnalyzer:
    def __init__(self, threshold = 3.0):
        self.threshold = threshold
        self.mean_vector = None
        self.inv_cov_matrix = None

    def set_standard_pose(self, mean_vector, inv_cov_matrix):
        self.mean_vector = mean_vector
        self.inv_cov_matrix = inv_cov_matrix

    def analyze(self, landmarks):
        # 실시간 감시 및 판정
        if self.mean_vector is None:
            return "UNKNOWN", 0.0
        
        current_vector = extract_features(landmarks)

        # 차이 벡터
        diff = current_vector - self.mean_vector

        # 마할라노비스 거리 계산: (diff^T * inv_cov * diff)
        left_term = np.dot(diff, self.inv_cov_matrix)
        mahalanobis_sq = np.dot(left_term, diff)

        dist = np.sqrt(max(mahalanobis_sq, 0.0))


        print(f"DEBUG: 거리={dist:.4f} / 기준={self.threshold} / 결과={dist < self.threshold}")

        if dist < self.threshold:
            return "Focused", dist
        
        else:
            return "Distracted", dist