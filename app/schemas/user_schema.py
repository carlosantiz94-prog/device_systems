# app/schemas/user_schema.py
# Modelos de datos (Pydantic v2) para validar entradas y estructurar salidas

from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Correo electronico unico del usuario")
    role: Literal["admin", "support", "user"] = Field(..., description="Rol del usuario en el sistema")
    is_active: bool = Field(default=True, description="Indica si el usuario esta activo")


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr] = Field(None)
    role: Optional[Literal["admin", "support", "user"]] = Field(None)
    is_active: Optional[bool] = Field(None)


class UserResponse(UserBase):
    id: int = Field(..., description="Identificador unico del usuario")

    class Config:
        from_attributes = True