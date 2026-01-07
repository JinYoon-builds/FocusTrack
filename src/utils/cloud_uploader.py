import requests
import json

class CloudUploader:
    """
    CloudUploader의 Docstring
    [동기화] 세션 데이터를 AWS API gateway로 전송합니다.
    """
    def __init__(self, api_url):
        self.api_url = api_url
        self.timeout = 5

    def upload_session(self, payload):

        if not payload:
            print("❌ 전송할 데이터 없음")
            return False
        
        headers = {'Content-Type' : 'application/json'}

        try:
            print(f"[Upload] 데이터 전송 시작... (size: {len(str(payload))})")

            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                print(f"✅ [Upload] 전송 성공!")
                return True
            
            else:
                print(f"❌ [Upload] 전송 실패! 오류 코드: {response.status_code}, 사유: {response.text}")
                return False


        except requests.exceptions.Timeout:
            print(f"❌ [Upload] 전송 실패! 시간 초과.")
            return False
        
        except requests.exceptions.ConnectionError:
            print(f"❌ [Upload] 전송 실패! 인터넷 연결 확인.")
            return False
        
        except Exception as e:
            print(f"❌ [Upload] 알 수 없는 오류 발생: {e}")
            return False