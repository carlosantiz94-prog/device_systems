# app/schemas/user_schema.py
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(..., min_length=3)
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool = Field(default=True)


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr] = None
    role: Optional[Literal["admin", "support", "user"]] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)