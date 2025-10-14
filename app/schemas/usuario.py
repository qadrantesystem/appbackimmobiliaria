from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    """Schema base de Usuario"""
    email: EmailStr
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    dni: Optional[str] = Field(None, max_length=20)

class UsuarioCreate(UsuarioBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=6)
    perfil_id: int = 1  # Por defecto demandante

class UsuarioUpdate(BaseModel):
    """Schema para actualizar usuario"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    dni: Optional[str] = Field(None, max_length=20)

class UsuarioUpdatePassword(BaseModel):
    """Schema para cambiar contraseña"""
    password_actual: str
    password_nueva: str = Field(..., min_length=6)
    password_confirmacion: str

class UsuarioResponse(UsuarioBase):
    """Schema de respuesta de Usuario"""
    usuario_id: int
    perfil_id: int
    perfil_nombre: Optional[str] = None
    estado: str
    fecha_registro: datetime
    plan_actual: Optional[str] = None
    
    class Config:
        from_attributes = True

class UsuarioListResponse(BaseModel):
    """Schema para lista de usuarios"""
    usuario_id: int
    email: str
    nombre: str
    apellido: str
    telefono: Optional[str]
    perfil_nombre: str
    estado: str
    fecha_registro: datetime
    plan_actual: Optional[str]
    
    class Config:
        from_attributes = True
