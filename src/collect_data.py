import tensorflow.lite as tflite
print("✅ [1/5] TensorFlow 로딩 완료!")

import time
import os
import cv2
import numpy as np

print("🎉 [준비 완료] 카메라 연결을 시도합니다.")

# ==========================================
# [설정] 카메라 번호 (보통 1번이 연동 카메라, 안 되면 0번)
CAMERA_INDEX = 1  
# ==========================================

# 1. 모델 로드
try:
    interpreter = tflite.Interpreter(model_path="mobilenet_v2_headless.tflite")
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
except Exception as e:
    print(f"❌ 모델 파일 오류: {e}")
    print("create_model.py를 먼저 실행해서 파일을 만들어주세요.")
    exit()

# 2. 데이터 저장소
study_data = []
distraction_data = []

# 3. 카메라 실행 (안전하게 켜기)
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_AVFOUNDATION)

# 🔥 카메라 예열 (맥북 카메라가 켜질 때까지 3초간 기다려줌)
print("🔥 카메라 예열 중... (화면이 나올 때까지 잠시 대기)")
for i in range(15):
    cap.read()
    time.sleep(0.1)

# 1번 실패 시 0번으로 자동 재시도
if not cap.isOpened() or not cap.read()[0]:
    print(f"⚠️ {CAMERA_INDEX}번 실패. 0번으로 재시도합니다.")
    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    for i in range(15): # 0번도 예열
        cap.read()
        time.sleep(0.1)

if not cap.isOpened():
    print("❌ 카메라 연결 실패. VS Code를 완전히 껐다가 다시 켜주세요 (리소스 점유 문제).")
    exit()

# 4. 화면 설정
window_name = 'FocusTrack Data Collector'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

print("\n" + "="*50)
print("   📸 [촬영 시작]   ")
print("   👉 공부 자세: 화면 클릭 후 키보드 [0] 연타")
print("   👉 딴짓 자세: 화면 클릭 후 키보드 [1] 연타")
print("   👉 종료 저장: 키보드 [q]")
print("="*50 + "\n")

while True:
    ret, frame = cap.read()
    
    # 잠깐 끊겨도 바로 꺼지지 않게 방어
    if not ret:
        print("⚠️ 신호 대기 중...", end='\r')
        time.sleep(0.1)
        continue

    # 정보 표시 (현재 몇 장 모았는지)
    info = f"Study(0): {len(study_data)} | Distraction(1): {len(distraction_data)}"
    
    # 텍스트 그림자 효과 (잘 보이게)
    cv2.putText(frame, info, (12, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4)
    cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.imshow(window_name, frame)
    
    key = cv2.waitKey(1) & 0xFF
    
    # 데이터 수집 (0번 또는 1번)
    if key == ord('0') or key == ord('1'):
        # 이미지 전처리 (AI가 좋아하는 형태로 변환)
        resized = cv2.resize(frame, (224, 224))
        input_data = np.expand_dims(resized, axis=0)
        # 이미지 데이터를 -1.0에서 1.0 사이로 조절
            # 색상값이 0~255이기 때문
        input_data = (input_data.astype(np.float32) / 127.5) - 1.0
        
        # 특징 추출
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        vector = interpreter.get_tensor(output_details[0]['index'])[0]
        
        if key == ord('0'):
            study_data.append(vector)
            print(f"📸 [공부] 찰칵! (현재 {len(study_data)}장)")
        elif key == ord('1'):
            distraction_data.append(vector)
            print(f"📸 [딴짓] 찰칵! (현재 {len(distraction_data)}장)")
            
    # 종료 (q)
    elif key == ord('q'):
        if len(study_data) == 0 and len(distraction_data) == 0:
            print("⚠️ 데이터가 없습니다! 저장하지 않고 종료합니다.")
        else:
            print("\n💾 데이터 저장 중...")
            np.savez('training_data.npz', study=study_data, distraction=distraction_data)
            print(f"✅ 저장 완료! (공부: {len(study_data)}장, 딴짓: {len(distraction_data)}장)")
            print("👉 이제 main.py를 실행할 차례입니다.")
        break

cap.release()
cv2.destroyAllWindows()