"""
🏢 Schemas para generación masiva de oficinas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

class CaracteristicaOficina(BaseModel):
    """Característica individual de oficina"""
    caracteristica_id: int = Field(..., description="ID de la característica")
    valor: str = Field(..., description="Valor de la característica")

class PlantillaOficina(BaseModel):
    """Plantilla para generar oficinas por piso"""
    sufijo: str = Field(..., description="Sufijo de oficina (01, 02, 03, etc.)", min_length=2, max_length=3)
    area: Decimal = Field(..., gt=0, description="Área en m²")
    caracteristicas: List[CaracteristicaOficina] = Field(default_factory=list, description="Características específicas")

class GenerarOficinasRequest(BaseModel):
    """Request para generar oficinas masivamente"""
    edificio_id: int = Field(..., description="ID del edificio padre")
    piso_desde: int = Field(..., ge=1, le=100, description="Piso inicial")
    piso_hasta: int = Field(..., ge=1, le=100, description="Piso final")
    plantilla_oficinas: List[PlantillaOficina] = Field(..., min_items=1, description="Plantilla de oficinas por piso")
    precio_alquiler_base: Optional[Decimal] = Field(None, ge=0, description="Precio base de alquiler")
    precio_venta_base: Optional[Decimal] = Field(None, ge=0, description="Precio base de venta")
    moneda: str = Field(default="PEN", pattern="^(PEN|USD)$")
    transaccion: str = Field(default="alquiler", pattern="^(alquiler|venta|ambos)$")
    propietario_id: int = Field(..., description="ID del propietario")
    distrito_id: int = Field(..., description="ID del distrito")

class OficinaGenerada(BaseModel):
    """Detalle de oficina generada"""
    registro_cab_id: int
    nombre_inmueble: str
    piso: int
    area: Decimal

class GenerarOficinasResponse(BaseModel):
    """Response de generación masiva"""
    oficinas_creadas: int = Field(..., description="Total de oficinas creadas")
    edificio_padre: str = Field(..., description="Nombre del edificio padre")
    detalles: List[OficinaGenerada] = Field(..., description="Detalle de oficinas creadas")

class EdificioDisponible(BaseModel):
    """Edificio disponible para selector"""
    registro_cab_id: int
    nombre_inmueble: str
    direccion: str
    tipo_inmueble_id: int  # ✅ ID del tipo de inmueble (para filtros)
    cantidad_pisos: Optional[str] = None  # Viene de características

    class Config:
        from_attributes = True
