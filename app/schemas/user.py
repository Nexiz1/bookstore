from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int

    class Config:
        from_attributes = True

class User(UserInDB):
    pass
