from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DeviceBase(BaseModel):
    name: str = Field(..., examples=["Laptop Lenovo ThinkPad"])
    serial_number: str = Field(..., examples=["LEN-2024-001"])
    device_type: str = Field(..., examples=["laptop"])
    brand: Optional[str] = Field(default=None, examples=["Lenovo"])
    is_available: bool = Field(default=True, examples=[True])


class DeviceCreate(DeviceBase):
    """Datos requeridos para registrar un nuevo dispositivo."""


class DeviceUpdate(DeviceBase):
    """Reemplazo completo del dispositivo (PUT)."""


class DevicePatch(BaseModel):
    """Actualizacion parcial del dispositivo (PATCH)."""
    name: Optional[str] = None
    serial_number: Optional[str] = None
    device_type: Optional[str] = None
    brand: Optional[str] = None
    is_available: Optional[bool] = None


class DeviceResponse(DeviceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
