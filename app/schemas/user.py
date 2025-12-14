from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    USER = "user"
    SELLER = "seller"
    ADMIN = "admin"


# ============ Request Schemas ============
class UserCreate(BaseModel):
    """회원가입 요청"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., max_length=20)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)


class UserLogin(BaseModel):
    """로그인 요청"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """프로필 수정 요청"""
    name: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    gender: Optional[str] = Field(None, max_length=10)


class PasswordChange(BaseModel):
    """비밀번호 변경 요청"""
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserRoleUpdate(BaseModel):
    """권한 변경 요청 (Admin용)"""
    role: UserRole


# ============ Response Schemas ============
class UserResponse(BaseModel):
    """사용자 정보 응답"""
    id: int
    email: str
    name: str
    role: UserRole
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """사용자 목록 응답 (Admin용)"""
    users: list[UserResponse]
    total: int
    page: int
    size: int
