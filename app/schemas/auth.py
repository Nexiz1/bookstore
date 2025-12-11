from typing import Optional

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """토큰 재발급 요청"""
    refresh_token: str


class TokenData(BaseModel):
    """토큰 데이터 (내부 사용)"""
    user_id: Optional[int] = None
    role: Optional[str] = None
