# ==============================================================================
# 역할 B: HTTP 파서 및 필터 모듈
# 작성자: 설건호
# 역할 A(네트워크)가 전달해 준 바이트 데이터를 분석해 핵심 주소와 차단 여부를 반환합니다.
# ==============================================================================

# [차단할 유해 사이트 목록]
# O(1)의 빠른 검색 속도를 위해 리스트[]가 아닌 세트{} 자료형을 사용했습니다.
BLACKLIST = {"warning.or.kr", "game.com", "gambling.com"}

def parse_http_request(request_data):
    """
    브라우저가 프록시로 보낸 HTTP 바이트(bytes) 데이터를 파싱합니다.
    
    [입력값 (Args)]
        request_data (bytes): 역할 A가 소켓을 통해 수신한 날것의 HTTP 요청 바이트
        
    [출력값 (Returns)]
        dict: 파싱이 성공하면 아래 형태의 딕셔너리를 반환하고, 실패하면 None을 반환합니다.
        {
            "method": "GET",                   # HTTP 메서드 (GET, POST 등)
            "host": "example.com",             # 목적지 도메인 또는 IP
            "port": 80,                        # 접속 포트 번호 (int)
            "url": "http://example.com/...",   # 캐시 창고의 Key(이름표)로 쓸 전체 URL
            "is_blocked": False                # 블랙리스트 차단 여부 (True면 차단)
        }
    """
    
    # 1. 바이트를 파이썬에서 다루기 편한 문자열(String)로 디코딩
    try:
        request_text = request_data.decode('utf-8')
    except UnicodeDecodeError:
        # 비표준 문자가 섞여 utf-8 에러가 날 경우를 대비한 방어 코드
        request_text = request_data.decode('ISO-8859-1')

    # 2. HTTP 요청문은 줄바꿈(\r\n)으로 구분됨. 가장 중요한 첫 줄(Request-Line)만 추출
    lines = request_text.split('\r\n')
    first_line = lines[0]

    # 첫 줄 예시: "GET http://example.com/ HTTP/1.1" -> 공백 기준으로 분리
    parts = first_line.split(' ')
    if len(parts) < 3:
        return None # 유효하지 않은 포맷이면 None 반환

    method = parts[0]
    url = parts[1]    

    # 3. 도메인(Host) 추출을 위해 'http://' 접두사 제거
    temp_url = url
    if temp_url.startswith("http://"):
        temp_url = temp_url[7:] 

    # 'example.com:8080/path/to/file' 형태에서 첫 번째 '/'를 기준으로 도메인 부분만 잘라냄
    host_port_path = temp_url.split('/', 1)
    host_port = host_port_path[0] 

    # 4. 포트(Port) 번호 솎아내기
    if ':' in host_port:
        # 주소에 포트가 명시된 경우 (예: example.com:9000)
        host, port_str = host_port.split(':', 1)
        port = int(port_str)
    else:
        # 명시되지 않은 일반 웹사이트는 HTTP 기본 통신 포트인 80으로 통일
        host = host_port
        port = 80

    # 5. 블랙리스트(차단) 여부 검사
    # 파싱해낸 host가 BLACKLIST 안에 있으면 True로 설정
    is_blocked = host in BLACKLIST

    # 6. 다른 팀원들이 쓰기 좋게 딕셔너리로 묶어서 반환
    return {
        "method": method,
        "host": host,
        "port": port,
        "url": url,
        "is_blocked": is_blocked
    }


# ==============================================================================
# [독립 테스트용 코드]
# 이 파일(http_parser.py)을 직접 실행했을 때만 작동하며,
# 다른 파일에서 import 할 때는 이 아래 부분은 실행되지 않습니다.
# ==============================================================================
if __name__ == "__main__":
    # 팀원 A의 코드가 아직 없어도 내 로직을 테스트해 볼 수 있는 가짜 데이터
    safe_request = b"GET http://example.com/ HTTP/1.1\r\nHost: example.com\r\n\r\n"
    blocked_request = b"GET http://game.com/play HTTP/1.1\r\nHost: game.com\r\n\r\n"
    
    print("--- 1. 정상 사이트 파싱 테스트 ---")
    res1 = parse_http_request(safe_request)
    print(res1)
    
    print("\n--- 2. 블랙리스트 유해 사이트 테스트 ---")
    res2 = parse_http_request(blocked_request)
    print(res2)
