from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime


class CorredorAprobar(BaseModel):
    """Schema para aprobar un corredor"""
    comision_porcentaje: Decimal = Field(..., gt=0, le=100, description="Porcentaje de comisión que Qadrante recibe")
    fecha_vigencia_corredor: datetime = Field(..., description="Fecha hasta la cual está autorizado")


class CorredorRechazar(BaseModel):
    """Schema para rechazar un corredor"""
    motivo_rechazo: str = Field(..., min_length=10, description="Motivo del rechazo")
