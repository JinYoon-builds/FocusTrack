import cv2

class Camera():
    def __init__(self, camera_index = 1, width = 1280, height = 720):
        # for mac
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if not self.cap.isOpened():
            raise RuntimeError(f"❌ 카메라 {camera_index}번을 열 수 없습니다.")
        
    def read(self):
        ret, frame = self.cap.read()
        if not ret: return None
        return cv2.flip(frame, 1) #거울모드
        
    def release(self):
        self.cap.release()
        
