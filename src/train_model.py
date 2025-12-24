import numpy as np
import tensorflow.lite as tflite
from sklearn.neighbors import KNeighborsClassifier
import os
import joblib

print("AI 훈련 시작!")

# 데이터 로딩
print("Focustrack 시동...")

if not os.path.exists('training_data.npz'):
    print("데이터 파일 없음")
    exit()

print("데이터 불러오는 중...")
data = np.load('training_data.npz')

study_X = data['study']
distraction_X = data['distraction']

print(f"✅ 로딩 완료! (공부 데이터: {len(study_X)}개,  딴짓 데이터: {len(distraction_X)}개)")

# 라벨링: 공부는 0, 딴짓은 1
study_Y = np.zeros(len(study_X))
distraction_Y = np.ones(len(distraction_X))

X = np.concatenate((study_X, distraction_X), axis=0)
Y = np.concatenate((study_Y, distraction_Y), axis=0)

# 모델학습 KNN
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X, Y)

# 모델 저장
joblib.dump(knn, 'knn_model.pkl')
print("피클링 완료")