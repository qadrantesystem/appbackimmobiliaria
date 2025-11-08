from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class PropietarioBase(BaseModel):
    """Schema base de Propietario"""
    dni: str = Field(..., min_length=8, max_length=20, description="DNI del propietario (único)")
    nombre: str = Field(..., min_length=3, max_length=255, description="Nombre completo del propietario")
    telefono: str = Field(..., min_length=9, max_length=50, description="Teléfono de contacto")
    email: Optional[str] = Field(None, max_length=255, description="Email del propietario")
    notas: Optional[str] = Field(None, description="Notas adicionales sobre el propietario")

class PropietarioCreate(PropietarioBase):
    """Schema para crear propietario"""
    pass

class PropietarioUpdate(BaseModel):
    """Schema para actualizar propietario"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=255)
    telefono: Optional[str] = Field(None, min_length=9, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    notas: Optional[str] = None
    activo: Optional[bool] = None

class PropietarioResponse(PropietarioBase):
    """Schema de respuesta de Propietario"""
    propietario_id: int
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PropietarioBuscarResponse(BaseModel):
    """
    Schema para auto-fill en frontend (búsqueda por DNI)
    Si existe, devuelve datos completos
    Si no existe, frontend lo creará
    """
    propietario_id: int
    dni: str
    nombre: str
    telefono: str
    email: Optional[str] = None
    existe: bool = True

    class Config:
        from_attributes = True
