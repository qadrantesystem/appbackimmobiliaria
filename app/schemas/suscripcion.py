from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

class SuscripcionCreate(BaseModel):
    """Schema para crear suscripción"""
    plan_id: int
    metodo_pago: str = Field(..., max_length=50)
    numero_operacion: Optional[str] = Field(None, max_length=100)
    monto_pagado: Decimal = Field(..., gt=0)
    comprobante_pago: Optional[str] = None  # URL o base64

class SuscripcionAprobar(BaseModel):
    """Schema para aprobar/rechazar suscripción"""
    accion: str = Field(..., pattern="^(aprobar|rechazar)$")
    notas_admin: Optional[str] = None

class SuscripcionResponse(BaseModel):
    """Schema de respuesta de Suscripción"""
    suscripcion_id: int
    usuario_id: int
    plan_id: int
    plan_nombre: str
    estado: str
    fecha_inicio: Optional[datetime]
    fecha_fin: Optional[datetime]
    monto_pagado: Decimal
    metodo_pago: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SuscripcionDetalleResponse(SuscripcionResponse):
    """Schema de respuesta detallada de Suscripción"""
    usuario: dict
    plan: dict
    numero_operacion: Optional[str]
    comprobante_pago: Optional[str]
    transaccion_id: Optional[str]
    auto_renovar: bool
    
    class Config:
        from_attributes = True
