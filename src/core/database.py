import sqlite3
from datetime import datetime

class FocusLogger:
    def __init__(self, db_path="focustrack_db", buffer_size = 10):
        self.db_path = db_path
        self.buffer = []
        self.buffer_limit = buffer_size

        self.session_id = int(datetime.now().timestamp())

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

    
    def close(self):
        self.flush()
        print("✅ DB 연결 종료. ")