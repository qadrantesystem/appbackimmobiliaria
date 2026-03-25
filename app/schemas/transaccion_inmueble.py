from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date, datetime


class TransaccionCreate(BaseModel):
    tipo_transaccion: str
    estado_ocupacion: Optional[str] = None
    inquilino_nombre: Optional[str] = None
    inquilino_ruc: Optional[str] = None
    inquilino_contacto: Optional[str] = None
    inquilino_telefono: Optional[str] = None
    inquilino_email: Optional[str] = None
    parqueos_simples: Optional[int] = 0
    parqueos_dobles: Optional[int] = 0
    tipo_persona: Optional[str] = "natural"
    ocupante_id: Optional[int] = None
    corredor_id: Optional[int] = None
    comision_porcentaje: Optional[Decimal] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    precio_oficina: Optional[Decimal] = None
    precio_estacionamiento: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    moneda: Optional[str] = "USD"
    observaciones: Optional[str] = None


class TransaccionUpdate(BaseModel):
    tipo_transaccion: Optional[str] = None
    estado_ocupacion: Optional[str] = None
    inquilino_nombre: Optional[str] = None
    inquilino_ruc: Optional[str] = None
    inquilino_contacto: Optional[str] = None
    inquilino_telefono: Optional[str] = None
    inquilino_email: Optional[str] = None
    parqueos_simples: Optional[int] = None
    parqueos_dobles: Optional[int] = None
    tipo_persona: Optional[str] = None
    corredor_id: Optional[int] = None
    comision_porcentaje: Optional[Decimal] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    precio_oficina: Optional[Decimal] = None
    precio_estacionamiento: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    moneda: Optional[str] = None
    es_vigente: Optional[bool] = None
    observaciones: Optional[str] = None


class TransaccionResponse(BaseModel):
    transaccion_id: int
    registro_cab_id: int
    tipo_transaccion: str
    estado_ocupacion: Optional[str] = None
    inquilino_nombre: Optional[str] = None
    inquilino_ruc: Optional[str] = None
    inquilino_contacto: Optional[str] = None
    inquilino_telefono: Optional[str] = None
    inquilino_email: Optional[str] = None
    parqueos_simples: Optional[int] = 0
    parqueos_dobles: Optional[int] = 0
    tipo_persona: Optional[str] = None
    ocupante_id: Optional[int] = None
    corredor_id: Optional[int] = None
    comision_porcentaje: Optional[Decimal] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    precio_oficina: Optional[Decimal] = None
    precio_estacionamiento: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    moneda: Optional[str] = None
    es_vigente: bool
    observaciones: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
