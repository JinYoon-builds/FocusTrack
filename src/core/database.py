import sqlite3
from datetime import datetime

class FocusLogger:
    def __init__(self, db_path="focustrack_db", buffer_size = 10):
        self.db_path = db_path
        self.buffer = []
        self.buffer_limit = buffer_size

        self.session_id = int(datetime.now().timestamp())
        self.start_dt = datetime.now()

        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS focus_logs (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       session_id INTEGER,
                       date TEXT,
                       time TEXT,
                       is_focused INTEGER,
                       focus_rate REAL,
                       dist REAL
                       )
                       ''')
        
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS sessions(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       session_id INTEGER UNIQUE,
                       date TEXT,
                       start_time TEXT,
                       end_time TEXt,
                       total_seconds REAL,
                       focus_seconds REAL,
                       avg_focus_rate REAL
                       )
                       ''')
        
        conn.commit()
        conn.close()
        print(f"✅ db 준비 완료: {self.db_path} (세션 ID: {self.session_id})")

    def log(self, is_focused: bool, focus_rate : float, dist: float):
        # 데이터를 메모리 버퍼에 추가

        now_dt = datetime.now()
        date_str = now_dt.strftime("%Y-%m-%d")
        time_str = now_dt.strftime("%H:%M:%S")

        focus_val = 1 if is_focused else 0

        record = (self.session_id, date_str, time_str, focus_val, focus_rate, dist)
        self.buffer.append(record)

        if len(self.buffer) >= self.buffer_limit:
            self.flush()

    def flush(self):
        if not self.buffer:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.executemany('''
                INSERT INTO focus_logs(session_id, date, time, is_focused, focus_rate, dist)
                VALUES(?, ?, ?, ?, ?, ?)

            ''', self.buffer)

            conn.commit()
            conn.close()
            self.buffer = []
            print("✅ DB 저장 완료 및 버퍼 초기화.")

        except Exception as e:
            print(f"❌ DB 저장 중 에러 발생: {e}")

    def save_session_summary(self):
        # 공부 종료 시, 이번 세션의 통계를 계산하여 요약 테이블에 저장
        self.flush()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            #세션 데이터 통계 내기
            cursor.execute('''
                           SELECT count(*), sum(is_focused), avg(focus_rate)
                           FROM focus_logs
                           WHERE session_id = ?
                           ''', (self.session_id, ))
            
            row = cursor.fetchone() # row == (총 시간, 집중한 시간, 집중도 점수의 평균)
            total_count = row[0] if row[0] else 0
            focused_count = row[1] if row[1] else 0
            avg_rate = row[2] if row[2] else 0

            if total_count == 0:
                print("❌ 저장할 데이터가 없습니다.")
                return
            
            total_seconds = float(total_count)
            focus_seconds = float(focused_count)
            
            end_dt = datetime.now()
            date_str = self.start_dt.strftime("%Y-%m-%d")
            start_str = self.start_dt.strftime("%H:%M:%S")
            end_str = end_dt.strftime("%H:%M:%S")

            cursor.execute('''
                            INSERT OR REPLACE INTO sessions
                           (session_id, date, start_time, end_time, total_seconds, focus_seconds, avg_focus_rate)
                           VALUES (?, ?, ?, ?, ?, ?, ?)
                           ''', (self.session_id, date_str, start_str, end_str, total_seconds, focus_seconds, avg_rate))
            
            conn.commit()
            print(f"✅ [세션 저장 완료]: 총 {int(total_count)} 초 중 {int(focus_seconds)}초 집중함. ")

        except Exception as e:
            print(f"❌ 세션 요약 저장 실패: {e}")

        finally:
            conn.close()

    def get_today_stats(self):
        today_str = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                        SELECT sum(total_seconds), sum(focus_seconds)
                       From sessions
                       WHERE date = ?
                       ''', (today_str, ))
        
        row = cursor.fetchone()
        conn.close()

        total = row[0] if row[0] else 0
        focused = row[1] if row[1] else 0

        return total, focused

    
    def close(self):
        self.save_session_summary()
        print("✅ DB 연결 종료. ")