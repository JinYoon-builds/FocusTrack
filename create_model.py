import tensorflow as tf
import os
import ssl  

# 보안 인증서 검사 건너뛰기 설정
ssl._create_default_https_context = ssl._create_unverified_context

# 1. MobileNet V2 모델 불러오기
print("⏳ 모델 다운로드 및 변환 중... 잠시만 기다려주세요.")
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,     # 분류기(Head) 제거
    weights='imagenet',    # 사전 학습된 데이터 사용
    pooling='avg'          # 1280개 숫자 벡터로 변환
)

# 2. TFLite로 변환
converter = tf.lite.TFLiteConverter.from_keras_model(base_model)
tflite_model = converter.convert()

# 3. 파일로 저장
model_name = 'mobilenet_v2_headless.tflite'
with open(model_name, 'wb') as f:
    f.write(tflite_model)

print(f"✅ 성공! '{model_name}' 파일이 생성되었습니다.")