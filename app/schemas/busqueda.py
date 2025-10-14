from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class BusquedaCreate(BaseModel):
    """Schema para crear búsqueda"""
    tipo_inmueble_id: Optional[int] = None
    distritos_ids: Optional[List[int]] = []
    transaccion: Optional[str] = Field(None, pattern="^(alquiler|venta)$")
    precio_min: Optional[Decimal] = Field(None, ge=0)
    precio_max: Optional[Decimal] = Field(None, ge=0)
    area_min: Optional[Decimal] = Field(None, ge=0)
    area_max: Optional[Decimal] = Field(None, ge=0)
    habitaciones: Optional[List[int]] = []
    banos: Optional[List[int]] = []
    parqueos_min: Optional[int] = Field(None, ge=0)
    filtros_avanzados: Optional[dict] = {}

class BusquedaGuardar(BaseModel):
    """Schema para guardar búsqueda (alerta)"""
    busqueda_id: Optional[int] = None
    nombre_busqueda: str = Field(..., min_length=3, max_length=100)
    frecuencia_alerta: str = Field(..., pattern="^(inmediata|diaria|semanal)$")
    alerta_activa: bool = True
    # Criterios de búsqueda (igual que BusquedaCreate)
    tipo_inmueble_id: Optional[int] = None
    distritos_ids: Optional[List[int]] = []
    transaccion: Optional[str] = None
    precio_min: Optional[Decimal] = None
    precio_max: Optional[Decimal] = None
    area_min: Optional[Decimal] = None
    area_max: Optional[Decimal] = None
    habitaciones: Optional[List[int]] = []
    banos: Optional[List[int]] = []
    parqueos_min: Optional[int] = None
    filtros_avanzados: Optional[dict] = {}

class BusquedaAlertaUpdate(BaseModel):
    """Schema para actualizar alerta"""
    alerta_activa: bool

class BusquedaResponse(BaseModel):
    """Schema de respuesta de Búsqueda"""
    busqueda_id: int
    tipo_inmueble: Optional[str]
    distritos: Optional[List[str]]
    transaccion: Optional[str]
    precio_max: Optional[Decimal]
    cantidad_resultados: Optional[int]
    fecha_busqueda: datetime
    
    class Config:
        from_attributes = True

class BusquedaGuardadaResponse(BusquedaResponse):
    """Schema de respuesta de Búsqueda Guardada"""
    nombre_busqueda: str
    frecuencia_alerta: str
    alerta_activa: bool
    ultima_notificacion: Optional[datetime]
    total_notificaciones: int
    
    class Config:
        from_attributes = True
