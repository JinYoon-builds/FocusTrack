# ADR-004: Edge-to-Cloud Data Transmission Strategy

* <b>Status:</b> Accepted
* <b>Date:</b> 2026-01-04
* <b>Author:</b> Jin Yoon
* <b>Context:</b> [ADR-003 Serverless Architecture]

## 1. 배경 (Context)
FocusTrack의 엣지 디바이스(RPi)는 학습 데이터를 생성하며, 이를 클라우드(AWS)로 전송해야 한다.
데이터 전송 방식에는 크게 두 가지 선택지가 존재했다.

1.  <b>Real-time Streaming (실시간 스트리밍):</b> MQTT/WebSocket 등을 이용해 1초 단위로 데이터를 계속 전송. (오토바이 배달)
2.  <b>Batch Processing (배치 처리):</b> 학습 세션이 끝날 때까지 로컬에 모아뒀다가 한 번에 전송. (이삿짐 트럭)

## 2. 의사결정 (Decision)
우리는 **배치 처리(Batch Processing)** 방식을 채택한다.
구체적으로는 **"Session-based Batch Upload"** 전략을 사용하며, 사용자가 학습 종료(Stop) 트리거를 발동시키는 시점에 `HTTP POST` 요청으로 누적 데이터를 전송한다.

## 3. 근거 (Justification)

### A. Serverless 아키텍처와의 호환성 (Compatibility)
* <b>AWS Lambda</b>는 이벤트 구동(Event-driven) 방식이므로, 24시간 연결을 유지해야 하는 스트리밍 방식(WebSocket)보다 단발성 요청을 처리하는 배치 방식에 최적화되어 있다.
* 스트리밍을 하려면 별도의 `API Gateway WebSocket API`나 `IoT Core`가 필요하여 인프라 복잡도가 증가한다.

### B. 비용 효율성 (Cost Efficiency)
* <b>Network Overhead:</b> HTTP 핸드셰이크 비용을 매초 발생시키는 것보다, 1시간에 1번 발생시키는 것이 훨씬 경제적이다.
* <b>Compute Cost:</b> Lambda 호출 횟수를 획기적으로 줄여 비용을 절감한다. (초당 1회 호출 vs 1시간당 1회 호출)

### C. 데이터 무결성 및 로컬 완결성 (Stability)
* 독서실 와이파이가 불안정할 경우, 실시간 전송은 데이터 유실(Packet Loss) 위험이 크다.
* 배치 방식은 로컬 메모리에 데이터를 안전하게 보관하다가, 네트워크가 연결되었을 때 확실하게(Retry 로직 포함) 보낼 수 있다.

## 4. 트레이드오프 및 보완책 (Trade-offs & Mitigations)

### 🚨 Critical Risk: 데이터 휘발성 (Data Volatility)
* <b>문제점:</b> 메모리(RAM)에만 데이터를 모아두는 방식은, 학습 도중 전원 차단이나 SW 크래시 발생 시 **진행 중이던 모든 데이터가 소실**될 위험이 있다. (예: 10시간 학습 데이터 증발)
* <b>해결책 (Mitigation): 로컬 지속성 (Local Persistence) & 동기화 플래그</b>
    1.  <b>Write-Through Logging:</b> 데이터를 생성하는 즉시 로컬 스토리지(SQLite/CSV)에 기록한다. (비동기 I/O 활용하여 성능 저하 최소화)
    2.  <b>Sync Status Flag:</b> 로컬 DB에 `is_uploaded` 컬럼을 둔다. (기본값: `False`)
    3.  <b>Recovery on Boot:</b> 프로그램 재실행 시, `is_uploaded=False`인 과거 세션이 발견되면 자동으로 재전송을 시도한다.

### ⚠️ Latency (지연 시간)
* <b>문제점:</b> 학부모나 관리자가 실시간으로 학생의 상태를 확인할 수 없다.
* <b>수용 근거:</b> 현재 MVP의 핵심 가치는 "감시"가 아닌 "자기 주도적 기록"이므로, 실시간성은 후순위로 미룬다.

## 5. 결론 (Result)
* 배치 처리를 기본으로 하되, **안정성(Stability)** 확보를 위해 **'로컬 저장 후 전송'** 패턴을 구현한다.
* 이를 통해 네트워크가 끊긴 상황(Offline)에서도 데이터 유실 없이 서비스를 지속할 수 있다.