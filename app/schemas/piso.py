from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class PisoCreate(BaseModel):
    numero_piso: int
    tipo_uso: Optional[str] = None
    area_total: Optional[Decimal] = None
    area_comercializable: Optional[Decimal] = None
    cantidad_unidades: Optional[int] = None
    activo: bool = True


class PisoUpdate(BaseModel):
    tipo_uso: Optional[str] = None
    area_total: Optional[Decimal] = None
    area_comercializable: Optional[Decimal] = None
    cantidad_unidades: Optional[int] = None
    activo: Optional[bool] = None


class PisoResponse(BaseModel):
    piso_id: int
    registro_cab_id: int
    numero_piso: int
    tipo_uso: Optional[str] = None
    area_total: Optional[Decimal] = None
    area_comercializable: Optional[Decimal] = None
    cantidad_unidades: Optional[int] = None
    activo: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
