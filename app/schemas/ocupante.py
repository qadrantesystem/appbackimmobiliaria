from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class OcupanteBase(BaseModel):
    """Schema base de Ocupante de Inmueble"""
    dni: str = Field(..., min_length=8, max_length=20, description="DNI del ocupante (unico)")
    nombre: str = Field(..., min_length=3, max_length=255, description="Nombre completo del ocupante")
    telefono: str = Field(..., min_length=9, max_length=50, description="Telefono de contacto")
    email: Optional[str] = Field(None, max_length=255, description="Email del ocupante")
    tipo_persona: Optional[str] = Field("natural", max_length=20, description="Tipo de persona: natural o juridica")
    empresa: Optional[str] = Field(None, max_length=255, description="Nombre de la empresa (si tipo_persona es juridica)")
    notas: Optional[str] = Field(None, description="Notas adicionales sobre el ocupante")

class OcupanteCreate(OcupanteBase):
    """Schema para crear ocupante"""
    pass

class OcupanteUpdate(BaseModel):
    """Schema para actualizar ocupante - DNI no se puede cambiar"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=255)
    telefono: Optional[str] = Field(None, min_length=9, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    tipo_persona: Optional[str] = Field(None, max_length=20)
    empresa: Optional[str] = Field(None, max_length=255)
    notas: Optional[str] = None
    activo: Optional[bool] = None

class OcupanteResponse(OcupanteBase):
    """Schema de respuesta de Ocupante"""
    ocupante_id: int
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OcupanteBuscarResponse(BaseModel):
    """
    Schema para auto-fill en frontend (busqueda por DNI)
    Si existe, devuelve datos completos
    Si no existe, frontend lo creara
    """
    ocupante_id: int
    dni: str
    nombre: str
    telefono: str
    email: Optional[str] = None
    tipo_persona: Optional[str] = None
    empresa: Optional[str] = None
    existe: bool = True

    class Config:
        from_attributes = True
