# Troubleshooting: Singular Matrix & Regularization 
<b>Date:</b> 2025-12-28
<b>Related Issue:</b> #9

## 1. Situation (상황)
캘리브레이션 단계에서 사용자가 움직임 없이 완벽하게 정지해 있을 경우, 시스템에 치명적인 오류가 발생함.
* <b>현상:</b> 마할라노비스 거리(Mahalanobis Distance) 결과값이 `22억` 같은 비정상적인 수치로 폭발하거나, `LinAlgError`가 발생함.

## 2. Task (과제)
이 현상은 **공분산 행렬(Covariance Matrix)의 역행렬**을 구하는 과정에서 발생함.
사용자의 움직임(분산)이 `0`에 수렴하여 수학적으로 계산이 불가능한 상태(Singular)를 해결해야 함.

## 3. Deep Dive Analysis (심층 분석)

### Q1. 분산이 0인데 왜 거리가 '0'이 아니라 '무한대(폭발)'가 되는가?
<b>A. 마할라노비스 거리의 정의 자체가 "분산으로 나누기"이기 때문임.</b>

* <b>직관적 이해:</b>
    * 유클리드 거리: $Distance = (x_2 - x_1)$
    * 마할라노비스 거리: $Distance = \frac{(x_2 - x_1)}{\text{표준편차}(\sigma)}$
* <b>수학적 원리:</b>
    * 공식: $D^2 = (x - \mu)^T \Sigma^{-1} (x - \mu)$
    * 여기서 $\Sigma^{-1}$ (역행렬)은 숫자에서의 **역수($1/\sigma^2$)**와 같은 역할을 함.
* <b>폭발 과정:</b>
    1. 사용자가 정지함 $\rightarrow$ 분산($\sigma^2$) $\approx 0.000000001$
    2. 역행렬($\Sigma^{-1}$) 계산 $\rightarrow$ $1 \div 0.000000001 = 1,000,000,000$ (10억)
    3. 거리 계산 $\rightarrow$ 아주 작은 차이에도 10억 배의 가중치가 곱해짐 $\rightarrow$ <b>22억 발생</b>

### Q2. Determinant(행렬식)가 0이 된다는 건 무슨 의미인가?
<b>A. 데이터가 차지하는 "부피(Volume)"가 사라져 차원이 붕괴되었음을 의미함.</b>



* <b>기하학적 의미:</b>
    * 행렬식($|A|$)은 행렬이 만드는 공간의 **부피**를 뜻함.
    * <b>정상 상태 ($|A| > 0$):</b> 데이터가 입체적으로 퍼져 있어 부피가 존재함 (풍선 모양).
    * <b>특이 상태 ($|A| = 0$):</b> 데이터가 납작하게 눌려 부피가 0이 됨 (종이짝 혹은 선 모양).
* <b>문제점:</b>
    * 부피가 0인 종이짝을 다시 원래의 풍선으로 되돌리는(역행렬) 연산은 불가능함.
    * 그래서 `LinAlgError: Singular matrix` (특이 행렬이라 계산 불가) 오류가 뜨는 것임.

### Q3. `np.eye(dim) * 0.01`은 수식적으로 어떤 작용을 하는가?
<b>A. 고유값(Eigenvalue) 강제 이동 (Shifting)</b>

* <b>배경:</b> 행렬식은 모든 고유값의 곱($\lambda_1 \times \lambda_2 \times \dots$)과 같음. 고유값이 하나라도 0이면 행렬식도 0이 됨.
* <b>해결 원리 (Ridge Regularization):</b>
    * 우리가 더해준 식: $\Sigma_{new} = \Sigma + 0.01I$
    * 이 연산은 행렬의 **모든 고유값에 0.01을 더해주는 효과**를 가짐.
    * $\lambda_{new} = \lambda_{old} + 0.01$
* <b>결과:</b>
    * 원래 고유값이 `0`이었던(움직임이 없던) 축도, 이제는 `0.01`이라는 값을 가지게 됨.
    * 따라서 행렬식은 절대 0이 되지 않음 (Always Invertible).
    * <b>의미:</b> "사용자가 아무리 가만히 있어도, 수학적으로는 최소한 0.01만큼은 숨 쉬고 있다"고 강제 정의하여 나눗셈 오류를 원천 차단함.

## 4. Action & Result (조치 및 결과)
* <b>Action:</b> 공분산 행렬 계산 직후 `Regularization term` 추가.
    ```python
    # 수학적 안전장치: 최소 분산(0.01) 주입
    cov_matrix += np.eye(cov_matrix.shape[0]) * 1e-2
    ```
* <b>Result:</b>
    * 정지 상태에서의 거리 값이 `NaN`이나 `INF`가 아닌 `0.5 ~ 1.5` 범위로 안정화됨.

    Engineering Decision: 0.01은 MediaPipe의 정규화된 좌표계(0~1 scale)에서 <b>센서 노이즈(Sensor Noise)</b>와 <b>생체 미세 떨림(Micro-movements)</b>을 상쇄하기 위해 실험적으로 도출한 임계값(Threshold)이다. 