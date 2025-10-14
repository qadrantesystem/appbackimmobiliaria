from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegister(BaseModel):
    """Schema para registro de usuario"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    dni: Optional[str] = Field(None, max_length=20)

class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema para token JWT"""
    access_token: str
    token_type: str = "bearer"
    usuario: dict

class TokenData(BaseModel):
    """Schema para datos del token"""
    usuario_id: Optional[int] = None
    email: Optional[str] = None
    perfil_id: Optional[int] = None
