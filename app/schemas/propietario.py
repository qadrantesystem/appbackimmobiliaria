from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class PropietarioBase(BaseModel):
    """Schema base de Propietario"""
    tipo_persona: Optional[Literal["natural", "juridica"]] = Field("natural", description="Tipo de persona")
    tipo_documento: Optional[Literal["DNI", "RUC", "CE", "PAS"]] = Field("DNI", description="Tipo de documento")
    dni: str = Field(..., min_length=8, max_length=20, description="DNI o documento del propietario")
    nombre: str = Field(..., min_length=3, max_length=255, description="Nombre completo o razón social")
    razon_social: Optional[str] = Field(None, max_length=255, description="Razón social (persona jurídica)")
    ruc: Optional[str] = Field(None, max_length=11, description="RUC (persona jurídica)")
    representante_legal: Optional[str] = Field(None, max_length=255, description="Representante legal")
    telefono: str = Field(..., min_length=9, max_length=50, description="Teléfono de contacto")
    email: Optional[str] = Field(None, max_length=255, description="Email del propietario")
    notas: Optional[str] = Field(None, description="Notas adicionales sobre el propietario")

class PropietarioCreate(PropietarioBase):
    """Schema para crear propietario"""
    pass

class PropietarioUpdate(BaseModel):
    """Schema para actualizar propietario"""
    tipo_persona: Optional[Literal["natural", "juridica"]] = None
    tipo_documento: Optional[Literal["DNI", "RUC", "CE", "PAS"]] = None
    nombre: Optional[str] = Field(None, min_length=3, max_length=255)
    razon_social: Optional[str] = Field(None, max_length=255)
    ruc: Optional[str] = Field(None, max_length=11)
    representante_legal: Optional[str] = Field(None, max_length=255)
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
    """Schema para auto-fill en frontend (búsqueda por DNI/RUC)"""
    propietario_id: int
    tipo_persona: Optional[str] = "natural"
    tipo_documento: Optional[str] = "DNI"
    dni: str
    nombre: str
    razon_social: Optional[str] = None
    ruc: Optional[str] = None
    representante_legal: Optional[str] = None
    telefono: str
    email: Optional[str] = None
    existe: bool = True

    class Config:
        from_attributes = True
