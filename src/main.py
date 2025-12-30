import cv2
import time

from core.analyzer import PoseCalibrator, FocusAnalyzer
from utils.camera import Camera
from core.pose_wrapper import PoseWrapper
from ui.renderer import Renderer
from core.database import FocusLogger

# 상태 머신 STATE MACHINE
STATE_WAITING = 0      # 준비
STATE_CALIBRATING = 1  # 측정 중
STATE_MONITORING = 2   # 감시 중

def main():
    # 카메라 불러오기
    try:
        camera = Camera(camera_index = 0, width=1920, height=1080)
        print("✅ 카메라 연결 성공!")
    except Exception as e:
        print(f"❌ 카메라 연결 실패: {e}")
        return
    
    # 캘리브레이터, 판정기 등 불러오기
    pose_wrapper = PoseWrapper()
    renderer = Renderer()

    FRAMES_PER_STEP = 30
    TOTAL_STEPS = 3
    calibrator = PoseCalibrator(buffer_size=FRAMES_PER_STEP * TOTAL_STEPS)

    analyzer = FocusAnalyzer(threshold=3.0)
    logger = FocusLogger(buffer_size=10)

    # 초기상태설정
    current_state = STATE_WAITING
    last_log_time = 0
    print("FocusTrack v2.0 시동... 캘리브레이션을 시작하려면 c를 누르세요.")
    calib_step = 1 # 1: 정자세, 2: 몰입(앞으로 기댐), 3: 이완(뒤로 기댐)
    is_measuring = False

    try:
        # 메인 루프
        fail_count = 0
        while True:
        # 입력
            frame = camera.read()
        
            if frame is None:
                fail_count += 1
                print(f"⚠️ 프레임 드랍 발생! ({fail_count}/10)")
            
                if fail_count > 10:
                    print("❌ 카메라 연결이 완전히 끊어졌습니다. 종료합니다.")
                    break
                # 이번 프레임은 건너뛰고 다시 시도
                continue

            # 처리: 뼈대 찾기
            results = pose_wrapper.process(frame)

            # 로직 & 출력
            if results.pose_landmarks:
                renderer.draw_skeleton(frame, results.pose_landmarks)

            # 상태별 로직
            # 1. 대기 화면
            if current_state == STATE_WAITING:
                renderer.draw_waiting(frame)

            # 2. 캘리브레이션 화면
            elif current_state == STATE_CALIBRATING:
                # 진행 상황
                current_count = len(calibrator.buffer)
                target_count = calib_step * FRAMES_PER_STEP

                # 측정 
                if is_measuring:
                    calibrator.add_data(results.pose_landmarks)
                    message = f"Step {calib_step}: Measuring..."

                    # 해당 스텝의 목표 달성 체크
                    if len(calibrator.buffer) >= target_count:
                        is_measuring = False
                        print(f"✅ Step {calib_step} 완료!")

                        # 수집 완료
                        if calib_step == TOTAL_STEPS:
                            print("✅ 캘리브레이션 완료.")
                            # 통계치 계산
                            mean_vec, inv_cov = calibrator.get_statistics()
                            analyzer.set_standard_pose(mean_vec, inv_cov)
                            current_state = STATE_MONITORING

                        else:
                            calib_step += 1


                # 대기
                else:  
                    if calib_step == 1:
                        message = "Step 1: Sit straight and Press 'c'"
                    elif calib_step == 2:
                        message = "Step 2: Lean forward and Press 'c'"
                    elif calib_step == 3:
                        message = "Step 3: Lean Back and Press 'c'"
                
                renderer.draw_calibration(frame, message, current_count, target_count)


            # 3. 분석 모드 화면 + logging
            # ‼️ 코어 로직 ‼️
            elif current_state == STATE_MONITORING:
                status, dist, focus_rate = analyzer.analyze(results.pose_landmarks)
                renderer.draw_monitoring(frame, status, dist)
                
                if time.time() - last_log_time >= 1.0:
                    is_focused_bool = (status == "FOCUSED")

                    logger.log(is_focused=is_focused_bool, focus_rate=focus_rate, dist=dist)

                    print(f"📝 Logged: {status} (Rate: {focus_rate:.2f})")

                    last_log_time = time.time()


            # 최종 화면 출력
            cv2.imshow('FocusTrack V2.1', frame)

            # 키보드 제어
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("프로그램을 종료합니다.")
                break
            elif key == ord('c'):
                # 처음 시작 시...
                if current_state == STATE_WAITING:
                    current_state = STATE_CALIBRATING
                    calib_step = 1
                    is_measuring = False
                # 단계별 측정 시작
                elif current_state == STATE_CALIBRATING and not is_measuring:
                    is_measuring = True
                    print(f"✅ Step {calib_step} 측정 시작...")

    finally:
        print("시스템 종료...")
        logger.close()
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()






     

