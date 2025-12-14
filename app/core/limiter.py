"""Rate Limiter 설정 모듈

slowapi를 사용한 Rate Limiting 설정.
순환 참조를 피하기 위해 별도 모듈로 분리.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate Limiter 초기화 (IP 주소 기반)
limiter = Limiter(key_func=get_remote_address)
