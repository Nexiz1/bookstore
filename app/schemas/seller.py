from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ============ Request Schemas ============
class SellerCreate(BaseModel):
    """판매자 등록 신청"""
    business_name: str = Field(..., max_length=32)
    business_number: str = Field(..., max_length=32)
    email: EmailStr
    address: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=32)
    payout_account: Optional[str] = Field(None, max_length=32)
    payout_holder: Optional[str] = None


class SellerUpdate(BaseModel):
    """판매자 정보 수정"""
    business_name: Optional[str] = Field(None, max_length=32)
    address: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=32)
    payout_account: Optional[str] = Field(None, max_length=32)
    payout_holder: Optional[str] = None


# ============ Response Schemas ============
class SellerResponse(BaseModel):
    """판매자 정보 응답"""
    id: int
    user_id: int
    business_name: str
    business_number: str
    email: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    payout_account: Optional[str] = None
    payout_holder: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
