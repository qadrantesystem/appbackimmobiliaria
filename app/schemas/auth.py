from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal

class UserRegister(BaseModel):
    """Schema para registro de usuario"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    dni: Optional[str] = Field(None, max_length=20)

    # Tipo de persona
    tipo_persona: Optional[Literal["natural", "juridica"]] = Field(default="natural")
    tipo_documento: Optional[Literal["DNI", "RUC", "CE", "PAS"]] = Field(default="DNI")

    # Datos de persona jurídica (opcionales)
    razon_social: Optional[str] = Field(None, max_length=255)
    ruc: Optional[str] = Field(None, max_length=11)
    representante_legal: Optional[str] = Field(None, max_length=255)

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
