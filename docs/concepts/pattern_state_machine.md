# 🧩 Tech Note: 유한 상태 머신 (Finite State Machine)

> <b>작성일:</b> 2025-12-30
> <b>관련 이슈:</b> #11 (Calibration Logic)
> <b>키워드:</b> Design Pattern, FSM, State Pattern, Architecture

---

## 1. 개요 (Overview)
FocusTrack의 사용자 인터랙션(대기 → 캘리브레이션 → 감시)을 제어하기 위해 <b>유한 상태 머신(FSM, Finite State Machine)</b> 패턴을 도입했다.
단순한 Boolean 플래그(`True/False`) 남발로 인한 논리적 오류를 방지하고, 프로그램의 흐름을 명확하게 제어하기 위함이다.

---

## 2. 도입 배경: 왜 상태 머신인가?

### 2.1 플래그(Flag) 변수의 문제점 (Boolean Hell)
상태 머신 없이 여러 변수로 상태를 관리할 경우, 논리적으로 불가능한 상태가 발생할 위험이 있다.
```python
# ❌ 나쁜 예: 논리적 모순 발생 가능
is_waiting = True
is_monitoring = True 
```

### 2.2 FSM의 해결책
시스템이 가질 수 있는 상태를 <b>상호 배타적(Mutually Exclusive)</b>인 상수로 정의하여, 한 시점에 오직 하나의 상태만 존재하도록 강제한다.

```python
# ✅ FocusTrack 적용: 단일 변수로 제어
current_state = STATE_WAITING 
# 0(대기), 1(측정), 2(감시) 중 하나만 가질 수 있음. 모순 원천 차단.
```

## 3. FocusTrack 구현 상세
### 3.1 상태 정의 (States)
- <b>STATE_WAITING (0):</b> 프로그램 시작 직후, 사용자 입력을 대기하는 상태.
- <b>STATE_CALIBRATING (1):</b> 'c' 키 입력 후, 3단계(정자세/몰입/이완) 데이터를 수집하는 상태.
- <b>STATE_MONITORING (2):</b> 데이터 수집 완료 후, 실시간으로 집중도를 분석하고 로깅하는 상태.

### 3.2 상태 전이 (Transition Flow)
```
stateDiagram-v2
    direction LR
    [*] --> WAITING: Start
    WAITING --> CALIBRATING: User input ('c')
    CALIBRATING --> CALIBRATING: Step 1 → 2 → 3
    CALIBRATING --> MONITORING: Calibration Complete
    MONITORING --> [*]: User input ('q')
```

### 3.3 구현 방식 (Procedural FSM)
현재는 main.py 내에서 current_state 변수와 if-elif 구조를 사용하여 상태를 분기 처리하는 방식을 사용 중이다. 이는 MVP 단계에서 직관적이고 빠른 구현이 가능하다.

## 4. 발전 방향: 상태 패턴 (State Pattern)
향후 로직이 복잡해질 경우, 객체지향의 <b>상태 패턴(State Design Pattern)</b>으로 리팩토링할 계획이다.
- <b>Context (Main):</b> 상태를 관리하는 변수만 보유하고, 실제 동작은 위임(Delegation)한다.
- <b>State (Classes):</b> WaitingState, MonitoringState 등 각 상태를 클래스로 분리하여 캡슐화한다.
- <b>장점:</b> main.py의 복잡도를 낮추고, 새로운 상태(예: 휴식 모드) 추가 시 기존 코드를 수정할 필요가 없다(OCP 원칙 준수).

