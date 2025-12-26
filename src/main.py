import cv2

from core.analyzer import PoseCalibrator, FocusAnalyzer
from utils.camera import Camera
from core.pose_wrapper import PoseWrapper
from ui.renderer import Renderer

# 상태 상수
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
    calibrator = PoseCalibrator(buffer_size=30)
    analyzer = FocusAnalyzer(threshold=0.05)

    # 초기상태설정
    current_state = STATE_WAITING
    print("FocusTrack v2.0 시동... 캘리브레이션을 시작하려면 c를 누르세요.")

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

        # 처리: 빼대 찾기
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
                count = calibrator.add_data(results.pose_landmarks)

                renderer.draw_calibration(frame, count)

                # 데이터가 다 모이면 분석 모드로 전환
                if calibrator.is_ready():
                    print("✅ 캘리브레이션 완료! 분석 모드로 전환...")

                    standard_pose = calibrator.get_standard_pose()
                    analyzer.set_standard_pose(standard_pose)

                    current_state = STATE_MONITORING

            # 3. 분석 모드 화면
            elif current_state == STATE_MONITORING:
                status, dist = analyzer.analyze(results.pose_landmarks)

                renderer.draw_monitoring(frame, status, dist)

        # 최종 화면 출력
        cv2.imshow('FocusTrack V2.0', frame)

        # 키보드 제어
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
           print("프로그램을 종료합니다.")
           break
        elif key == ord('c') and current_state == STATE_WAITING:
            print("사용자 캘리브레이션(최적화) 중...")
            current_state = STATE_CALIBRATING

    # 종료
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()






     

