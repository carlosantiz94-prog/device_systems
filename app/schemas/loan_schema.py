from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LoanBase(BaseModel):
    user_id: int = Field(..., examples=[1])
    device_id: int = Field(..., examples=[3])


class LoanCreate(LoanBase):
    """Datos requeridos para registrar un nuevo prestamo."""


class LoanUpdate(BaseModel):
    status: Optional[str] = None
    return_date: Optional[datetime] = None


class LoanResponse(BaseModel):
    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: Optional[datetime]
    status: str

    class Config:
        from_attributes = True


class UserBasic(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class DeviceBasic(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str

    class Config:
        from_attributes = True


class LoanDetailResponse(BaseModel):
    """Salida con informacion relacionada (JOIN entre loans, users y devices)."""
    loan_id: int
    status: str
    loan_date: datetime
    return_date: Optional[datetime]
    user: UserBasic
    device: DeviceBasic

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "loan_id": 1,
                "status": "active",
                "loan_date": "2026-09-16T10:00:00",
                "return_date": None,
                "user": {"id": 1, "name": "Ana Perez", "email": "ana@sena.edu.co"},
                "device": {
                    "id": 3,
                    "name": "Laptop Lenovo ThinkPad",
                    "serial_number": "LEN-2024-001",
                    "device_type": "laptop",
                },
            }
        }
