from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """표준화된 API 응답 포맷"""
    status: str
    data: Optional[T] = None
    message: Optional[str] = None


class SuccessResponse(BaseResponse[T], Generic[T]):
    """성공 응답"""
    status: str = "success"


class ErrorResponse(BaseModel):
    """표준 에러 응답 포맷

    과제 요구사항에 맞춘 에러 응답 규격:
    - timestamp: 에러 발생 시각
    - path: 요청 경로
    - status: HTTP 상태 코드
    - code: 에러 코드 (예: USER_NOT_FOUND)
    - message: 사용자 친화적 에러 메시지
    - details: 추가 에러 상세 정보 (Validation 에러 시 필드별 에러 등)
    """
    timestamp: str
    path: str
    status: int
    code: str
    message: str
    details: Optional[Any] = None


class HealthResponse(BaseModel):
    """헬스 체크 응답"""
    status: str
    version: str
    timestamp: str
