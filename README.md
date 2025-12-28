# 🎯 FocusTrack (MVP)

<div align="center">
  <img src="docs/images/logo.png" alt="FocusTrack Logo" width="200" height="200">
  <h1>FocusTrack</h1>
  <p>
    <b>Data-Driven Focus Management Solution for Academies with Computer Vision</b>
  </p>
</div>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Vision-0099CC?logo=google&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?logo=opencv&logoColor=white)
![RaspberryPi](https://img.shields.io/badge/Device-Raspberry_Pi-C51A4A?logo=raspberrypi&logoColor=white)
![Status|144x20](https://img.shields.io/badge/Status-In_Development-yellow)

<br/>

## 🌰 In a nutshell...
> **Data-Driven Focus Management Solution for Academies with Computer Vision**
> 
> 컴퓨터비전 기술을 사용해 학습자의 집중도를 실시간으로 측정 및 분석하여 학습 효율을 극대화하는 솔루션입니다.

<br/>

## 🧐 Problem & Solution

### ❓ The Problem
기존의 관리형 독서실이나 캠스터디 시스템은 단순히 <b>착석 여부(Quantity)</b>만을 관리합니다. 학부모는 학생이 등원했다는 사실만 알 수 있고, 학생은 자신이 정확히 얼마나 몰입했는지 모른 채 '오래 앉아 있었다'는 사실만으로 위안을 얻습니다.

### ❗️ Our Solution
**FocusTrack**은 컴퓨터 비전(Computer Vision) 기술을 활용해 사용자의 실제 학습 행동을 분석하고, **데이터 기반의 피드백**을 제공합니다.

- **Hyper-Personalization (초개인화):** 획일적인 자세 기준이 아닌, 사용자별 고유한 학습 자세를 캘리브레이션하여 판정합니다.
- **Privacy First:** 영상 데이터를 서버로 전송하지 않고, 디바이스 내에서 처리하는 온디바이스 AI(On-device AI)를 지향합니다.
- **Actionable Insight:** 단순 기록을 넘어, 집중도가 깨지는 시간대와 패턴을 분석한 **집중도 분석 리포트**를 제공합니다.

<br/>

## 🧠 Core Logic (Data Pipeline)

시스템은 크게 **Edge(수집/판정)** → **Server(가공/저장)** → <b>Client(시각화)</b>의 3단계로 작동합니다.

1.  **Input (Edge):** 웹캠을 통해 라즈베리파이(또는 PC)로 실시간 영상 스트림 입력.
2.  **Feature Extraction (MediaPipe):** 배경을 소거하고, 사용자의 관절 좌표(Landmark 33개)만을 추출.
3.  **Anomaly Detection (One-Class):** * **Calibration:** 시작 시 약 30초간 사용자의 '표준 공부 자세'를 수집하여 기준점(Centroid)을 생성.
    * **Distance Calculation:** 실시간 좌표가 기준점 임계값(Threshold)을 벗어나면 즉시 <b>'비집중(Outlier)'</b>으로 판정. (별도의 '딴짓' 데이터 학습 불필요)
4.  **Data Transmission:** 엣지 디바이스는 영상이 아닌, 판정된 결과값(`0` or `1`)과 타임스탬프만을 JSON 형태로 서버에 전송.
5.  **Data Aggregation (Server):** 서버는 수신된 시계열 데이터를 분석하여 **순수 집중 시간(Net Focus Time)**, **집중 유지 구간**, **이탈 빈도** 등을 가공.
6.  **Visualization (User):** 사용자는 웹 대시보드를 통해 시각화된 <b>'일간/주간 집중 리포트'</b>를 확인하고 학습 패턴을 점검.

<br/>

## 🛠 Project Status
![Development Status](https://img.shields.io/badge/Status-In%20Progress-yellow) 

현재 **MVP 개발 단계**입니다.

<br/>

## ⚙️ Tech Stack

| Category | Technology |
| --- | --- |
| **Language** | Python 3.11+ |
| **Vision AI** | MediaPipe Pose, OpenCV |
| **Algorithm** | NumPy (Vector Ops), Anomaly Detection |
| **Edge Device** | Raspberry Pi 4 / 5 (Target) |
| **Backend** | FastAPI (Planned) |
| **Frontend** | Streamlit (MVP) |

<br/>

## 📚 Engineering Wiki & Dev Log
프로젝트 진행 과정에서 고민한 기술적 의사결정과 문제 해결 과정을 기록했습니다.

### 🏗️ Architecture Decision Records (ADR)
주요 기술 스택 선정 및 아키텍처 변경에 대한 의사결정 내역입니다.
* [📂 ADR-001: 전체 이미지 분석(MobileNet)에서 좌표 기반 분석(MediaPipe)으로의 전환](docs/ADR/001_switch_to_mediapipe.md)
* [📂 ADR-002: 지도 학습(Binary Classification)에서 이상 탐지(Anomaly Detection)로의 전환](docs/ADR/002_shift_to_anomaly_detection.md)

### 📐 Core Concepts & Algorithms
프로젝트에 적용된 핵심 알고리즘과 수학적 배경지식입니다.
* [📝 Tech Note: 왜 유클리드 대신 '마할라노비스 거리'인가?](docs/concepts/math_mahalanobis_distance.md)
    * *좌표의 분산과 공분산을 고려한 통계적 거리의 도입 배경 및 원리*

### 🛠️ Troubleshooting
* [🐛 Fix: "거리 22억" 버그 - 특이 행렬(Singular Matrix)과 Regularization](docs/troubleshooting/ts_001_singular_matrix_fix.md)
* [🐛 Fix: Numpy 차원 불일치 문제와 .flatten() 활용](docs/troubleshooting/ts_002_numpy_flatten.md)

<br/>

## 🚀 Roadmap & Progress

- [x] **Ideation & Market Research**: 문제 정의 및 기존 솔루션 분석.
- [x] **Prototyping (Phase 1)**: MobileNet 기반 이미지 분류 모델 테스트 (-> *Background Noise 문제로 폐기*) (2025.12.19 ~ 2025.12.24)
- [ ] **MVP Development (Phase 2)**: MediaPipe + 이상 탐지(Calibration) 알고리즘 구현 및 로컬 시각화(Streamlit). **(~2026.02.09)**
- [ ] **Backend & Data Pipeline (Phase 3)**: FastAPI 서버 구축, 시계열 데이터 DB 설계, 집중도 분석 로직(순수 공부 시간 산출) 구현.
- [ ] **Hardware Porting (Phase 4)**: Raspberry Pi 포팅, 엣지-서버 통신 최적화 및 QR 로그인 시스템 구축.
- [ ] **B2B Deployment**: 관리형 독서실 환경 필드 테스트 및 피드백 반영.

<br/>

---
Contact: jin.yoon.builds@gmail.com