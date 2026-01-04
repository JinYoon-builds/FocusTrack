# ADR-003: 데이터 동기화를 위한 AWS Serverless 아키텍처 도입

* <b>Status:</b> Accepted
* <b>Date:</b> 2026-01-03
* <b>Author:</b> Jin Yoon

## 1. 배경 (Context)
FocusTrack은 엣지 디바이스(라즈베리파이/PC)에서 독립적으로 동작하는 온디바이스 AI 솔루션이다. MVP 단계에서 사용자의 학습 이력(Session Summary)을 웹 대시보드에서 시각화하기 위해, 로컬 데이터를 클라우드로 전송하고 저장하는 백엔드 인프라가 필요해졌다.

현재 프로젝트의 상황과 제약 조건은 다음과 같다.
1.  <b>트래픽 특성:</b> 사용자가 학습을 종료하는 시점에만 간헐적(Intermittent)으로 트래픽이 발생한다.(가장 중요)
2.  <b>리소스 제약:</b> 1인 개발 체제이므로 인프라 관리(OS 패치, 스케일링 등)에 쏟을 시간이 부족하다.
3.  <b>비용 효율성:</b> 초기 사용자 수가 적은 MVP 단계에서 고정적인 서버 비용(EC2 등) 지출을 최소화해야 한다.

## 2. 대안 분석 (Alternatives Considered)

### 대안 A: Traditional Server (EC2 + FastAPI + MySQL)
* <b>장점:</b> 개발 자유도가 높고, 복잡한 쿼리나 긴 작업(Long-running process) 처리에 유리하다.
* <b>단점:</b> 트래픽이 없어도 24시간 서버를 켜둬야 하므로 유휴 자원 비용이 발생한다. 오토 스케일링, 로드 밸런싱, 보안 패치 등을 직접 관리해야 하는 오버헤드(Operational Overhead)가 크다.

### 대안 B: Other NoSQL Solutions (e.g., MongoDB Atlas)
* <b>장점:</b> 쿼리 문법이 익숙하고, 복잡한 인덱싱 기능이 강력하다.
* <b>단점:</b> AWS Lambda와 연동 시 <b>Connection Pool 고갈 문제</b>가 발생하기 쉽다. Lambda 인스턴스가 순간적으로 수백 개 생성될 경우, DB 연결 수를 초과하여 장애가 발생할 수 있으며 이를 해결하기 위한 프록시 설정이 추가로 필요하다.

### 대안 C: Serverless Architecture (AWS Lambda + DynamoDB) 🏆
* <b>장점:</b>
    * <b>비용 최적화:</b> 코드가 실행되는 시간(ms 단위)만큼만 과금되므로, 간헐적 트래픽 환경에서 비용이 0에 수렴한다.
    * <b>NoOps:</b> 서버 관리 없이 비즈니스 로직(함수)에만 집중할 수 있다.
    * <b>완벽한 통합:</b> HTTP(Rest API) 기반 통신으로 Connection 관리가 불필요하며, IAM을 통한 권한 제어가 강력하다.
* <b>단점:</b> 콜드 스타트(Cold Start) 지연 시간이 존재하나, 비동기 데이터 업로드 방식이므로 사용자 경험에 영향을 주지 않는다.

## 3. 결정 (Decision)
우리는 <b>AWS Lambda(FaaS)와 Amazon DynamoDB(NoSQL)</b>를 활용한 <b>서버리스 아키텍처</b>를 채택한다. 특히 수많은 NoSQL 중 DynamoDB를 선정한 구체적인 이유는 다음과 같다.

1.  <b>Stateless Connection Model:</b>
    * MongoDB 등은 영구적인 연결(TCP Socket)을 맺어야 하므로, 수천 개의 Lambda가 동시에 실행될 때 DB 연결 한계(Connection Limit)에 도달하기 쉽다.
    * 반면 DynamoDB는 <b>HTTP Request 기반</b>으로 동작하므로, 동시 접속자가 폭증해도 연결 오버헤드 없이 무한 확장이 가능하다.
2.  <b>On-demand Capacity:</b>
    * 미리 용량을 프로비저닝할 필요 없이, 요청이 들어온 만큼만 자동으로 처리량을 조절하는 <b>On-demand Mode</b>를 지원하여 IoT 데이터의 불규칙한 패턴에 최적화되어 있다.
3.  <b>IAM Security Integration:</b>
    * DB 비밀번호를 코드에 하드코딩하거나 별도로 관리할 필요 없이, AWS IAM Role을 통해 Lambda 함수에 <b>최소 권한(Least Privilege)</b>만 부여하여 보안성을 극대화할 수 있다.

## 4. 결과 (Consequences)
* <b>Positive:</b>
    * 서버 유휴 비용을 100% 제거하여 MVP 운영 비용을 최소화했다.
    * 인프라 관리에 대한 부담을 덜고, 핵심 알고리즘(AI Model) 개선에 집중할 수 있게 되었다.
    * 전통적인 RDBMS나 MongoDB에서 발생하는 <b>Connection Pool 관리 이슈</b>를 원천적으로 제거했다.
* <b>Negative:</b>
    * AWS 생태계에 대한 종속성(Vendor Lock-in)이 증가했다.
    * 로컬 환경에서의 테스트와 디버깅이 기존 서버 방식보다 다소 까다로울 수 있다. (AWS SAM 등을 활용하여 보완 예정)