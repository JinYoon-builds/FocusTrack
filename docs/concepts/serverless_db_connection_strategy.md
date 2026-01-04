# Tech Note: Serverless 환경에서의 DB Connection 전략과 DynamoDB 선정 배경

* <b>Date:</b> 2026-01-03
* <b>Author:</b> Jin Yoon

## 1. 문제의 발견 (Problem Statement)
AWS Lambda 기반의 서버리스 아키텍처를 설계하던 중, 전통적인 RDBMS(MySQL 등)를 사용할 경우 <b>'Connection Pool Exhaustion (커넥션 고갈)'</b> 문제가 발생할 수 있음을 인지하였다.

## 2. 기술적 배경 (Technical Background)

### 2.1 Traditional Server (Stateful)
* 일반적인 서버(EC2, WAS)는 부팅 시 DB와 미리 일정 수(예: 10개)의 연결을 맺어두는 <b>Connection Pool</b>을 생성한다.
* 다수의 요청이 들어와도 이 10개의 연결을 재사용(Reuse)하므로, DB에 가해지는 연결 부하가 일정하다.

### 2.2 Serverless Function (Stateless)
* Lambda는 요청이 들어올 때마다 독립적인 컨테이너(실행 환경)가 뜬다.
* <b>Problem:</b> 만약 1,000명의 사용자가 동시에 학습을 종료하여 데이터를 전송한다면?
    * 1,000개의 Lambda 인스턴스가 생성됨.
    * 각 인스턴스가 DB에 `Connect()`를 시도함.
    * <b>Result:</b> RDBMS의 최대 연결 수(Max Connections)를 초과하여 `Too Many Connections` 에러 발생 및 서비스 장애.

## 3. 해결 방안 비교 (Solution Analysis)

이 문제를 해결하기 위해 두 가지 대안을 검토하였다.

### 대안 A: AWS RDS Proxy 도입
* <b>개념:</b> Lambda와 RDBMS 사이에 '중계기'를 두어 커넥션을 관리하게 하는 방식.
* <b>장점:</b> 기존 RDBMS(SQL)를 그대로 사용할 수 있음.
* <b>단점:</b>
    * 별도의 비용이 발생함.
    * VPC(가상 네트워크) 설정 등 인프라 구성이 복잡해짐 (MVP 단계에서 오버 엔지니어링).

### 대안 B: NoSQL (DynamoDB) 도입 🏆
* <b>개념:</b> HTTP API 요청(Stateless) 방식으로 데이터를 저장하는 NoSQL 사용.
* <b>장점:</b>
    * <b>Connectionless:</b> 연결을 맺고 끊는 과정(Handshake)이 아예 없음.
    * <b>Scalability:</b> 요청량이 폭증해도 AWS Request Router가 처리하므로 병목이 없음.
    * <b>IAM Integration:</b> 별도의 DB 계정/비번 관리 없이 IAM Role로 보안 처리 가능.

## 4. 결론 (Conclusion)
FocusTrack은 <b>"간헐적이지만 순간적인 트래픽 폭주"</b>가 발생할 수 있는 IoT 서비스다.
따라서 복잡한 인프라 관리 없이도 동시성 이슈를 원천 차단할 수 있는 <b>DynamoDB</b>가 가장 적합하다고 판단하였다.