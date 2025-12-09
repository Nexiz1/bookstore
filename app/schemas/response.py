from typing import TypeVar, Generic, Optional, Any
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
    """에러 응답"""
    status: str = "error"
    message: str
    data: Optional[Any] = None
