from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

class PlanBase(BaseModel):
    """Schema base de Plan"""
    nombre: str = Field(..., min_length=3, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)
    precio: Decimal = Field(..., ge=0)
    duracion_dias: int = Field(default=30, ge=1)
    limite_busquedas: int = Field(default=10, ge=-1)  # -1 = ilimitado
    limite_registros: int = Field(default=1, ge=-1)  # -1 = ilimitado

class PlanCreate(PlanBase):
    """Schema para crear plan"""
    pass

class PlanUpdate(BaseModel):
    """Schema para actualizar plan"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)
    precio: Optional[Decimal] = Field(None, ge=0)
    duracion_dias: Optional[int] = Field(None, ge=1)
    limite_busquedas: Optional[int] = Field(None, ge=-1)
    limite_registros: Optional[int] = Field(None, ge=-1)
    activo: Optional[bool] = None

class PlanResponse(PlanBase):
    """Schema de respuesta de Plan"""
    plan_id: int
    activo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
