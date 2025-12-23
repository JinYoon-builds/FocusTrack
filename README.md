# 🎯 FocusTrack (MVP)

> **Computer Vision Based Focus Monitoring System for Ed-Tech**
> 
> "기술로 가치를 창출한다" - 학습자의 집중도를 실시간으로 측정하여 학습 효율을 극대화하는 솔루션입니다.

## 🛠 Project Status
![Development Status](https://img.shields.io/badge/Status-In%20Progress-yellow) 현재 **MVP 개발 단계**에 있으며, 핵심 기능(Core Feature) 구현 및 검증을 진행 중입니다.

## 💡 Tech Stack
* **Language:** Python 3.11+
* **Vision:** OpenCV, MediaPipe (Hand/Face Mesh)
* **Hardware Target:** MacBook M3 Pro (Dev), Low-end Laptop (User)
* **Tools:** Git, VS Code

## 📝 Dev Log & ADR (Architecture Decision Records)
이 프로젝트는 단순한 구현을 넘어, **'문제 해결 과정'**을 기록합니다.
주요 기술적 의사결정과 트러블슈팅 내역은 아래에서 확인할 수 있습니다.

* [📂 docs/adr/001-model-selection.md](링크예정) : TensorFlow에서 MediaPipe로 피봇팅한 이유

## 🚀 Roadmap & Progress
- [x] 프로젝트 초기 세팅 및 Git 저장소 구축
- [x] 웹캠 영상 스트림 연동
- [ ] MediaPipe 손동작 인식 파이프라인 구축
- [ ] 집중도 판단 알고리즘 (눈 깜빡임, 고개 각도) 구현
- [ ] 실시간 데이터 로깅 시스템
- [ ] MVP 최종 테스트

---
Contact: jin.yoon.builds@gmail.com