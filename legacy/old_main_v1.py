import cv2
import numpy as np
import tensorflow.lite as tflite
import joblib
import time

print("✅ FOCUSTRACK 가동")

# 모델 로드
try:
    interpreter = tflite.Interpreter(model_path = "mobilenet_v2_headless.tflite")
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    knn = joblib.load('knn_model.pkl')

except Exception as e:
    print(f"❌ 모델 로딩 실패: {e}")

# 카메라 설정
CAMERA_INDEX = 1  
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_AVFOUNDATION)

while True:
    ret, frame = cap.read()
    if not ret: break

    # 이미지 전처리
    resized = cv2.resize(frame, (224, 224))
    input_data = np.expand_dims(resized, axis=0)
    input_data = (input_data.astype(np.float32) / 127.5) - 1.0

    # 특징 추출
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    vector = interpreter.get_tensor(output_details[0]['index'])[0]

    # 판정하기
    prediction = knn.predict([vector])

    if prediction[0] == 0:
        status = "Studing"
        color = (0, 255, 0)
    else:
        status = "Distraction"
        color = (255, 0, 0)

    # 화면 표시
    cv2.putText(frame, status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
    cv2.imshow('FocusTrack TF', frame)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()