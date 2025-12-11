import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    """HTTP 요청/응답 로깅 미들웨어"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # 요청 정보
        method = request.method
        path = request.url.path
        query = str(request.query_params) if request.query_params else ""

        # 요청 로깅
        if query:
            logger.info(f"→ {method} {path}?{query}")
        else:
            logger.info(f"→ {method} {path}")

        # 요청 처리
        response = await call_next(request)

        # 응답 시간 계산
        duration = time.time() - start_time
        duration_ms = duration * 1000

        # 응답 로깅 (상태 코드에 따라 로그 레벨 변경)
        status_code = response.status_code
        if status_code >= 500:
            logger.error(f"← {status_code} ({duration_ms:.2f}ms)")
        elif status_code >= 400:
            logger.warning(f"← {status_code} ({duration_ms:.2f}ms)")
        else:
            logger.info(f"← {status_code} ({duration_ms:.2f}ms)")

        return response
