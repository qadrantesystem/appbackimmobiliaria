from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class CaracteristicaDetalle(BaseModel):
    """Schema para característica en detalle"""
    caracteristica_id: int
    valor: str

class PropiedadBase(BaseModel):
    """Schema base de Propiedad"""
    # NUEVO: FK a propietario normalizado
    propietario_id: int = Field(..., description="ID del propietario (normalizado)")

    # NUEVO: Recursividad (opcional para oficinas)
    padre_registro_cab_id: Optional[int] = Field(None, description="ID del edificio padre (solo para oficinas)")
    piso: Optional[int] = Field(None, description="Número de piso (solo para oficinas/departamentos)")

    # Datos del inmueble
    tipo_inmueble_id: int
    distrito_id: int
    nombre_inmueble: str = Field(..., min_length=5, max_length=200)
    direccion: str = Field(..., min_length=10, max_length=300)
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None

    # Características básicas (solo transversales)
    area: Decimal = Field(..., gt=0)
    antiguedad: Optional[int] = Field(None, ge=0)

    # Precios
    transaccion: str = Field(..., pattern="^(alquiler|venta|ambos)$")
    precio_alquiler: Optional[Decimal] = Field(None, ge=0)
    precio_venta: Optional[Decimal] = Field(None, ge=0)
    moneda: str = Field(default="PEN", pattern="^(PEN|USD)$")
    
    # Descripción
    titulo: str = Field(..., min_length=10, max_length=200)
    descripcion: Optional[str] = None
    
    @validator('precio_alquiler', 'precio_venta')
    def validar_precios(cls, v, values):
        """Validar que al menos un precio esté presente"""
        if 'transaccion' in values:
            transaccion = values['transaccion']
            if transaccion == 'alquiler' and not values.get('precio_alquiler'):
                raise ValueError('precio_alquiler es requerido para transacción de alquiler')
            if transaccion == 'venta' and not values.get('precio_venta'):
                raise ValueError('precio_venta es requerido para transacción de venta')
        return v

class PropiedadCreate(PropiedadBase):
    """Schema para crear propiedad"""
    imagen_principal: Optional[str] = None
    imagenes: Optional[List[str]] = []
    caracteristicas: Optional[List[CaracteristicaDetalle]] = []

class PropiedadUpdate(BaseModel):
    """Schema para actualizar propiedad"""
    nombre_inmueble: Optional[str] = Field(None, min_length=5, max_length=200)
    direccion: Optional[str] = Field(None, min_length=10, max_length=300)
    area: Optional[Decimal] = Field(None, gt=0)
    antiguedad: Optional[int] = Field(None, ge=0)
    precio_alquiler: Optional[Decimal] = Field(None, ge=0)
    precio_venta: Optional[Decimal] = Field(None, ge=0)
    titulo: Optional[str] = Field(None, min_length=10, max_length=200)
    descripcion: Optional[str] = None
    imagen_principal: Optional[str] = None
    imagenes: Optional[List[str]] = None
    piso: Optional[int] = Field(None, description="Número de piso (solo para oficinas/departamentos)")

class PropiedadEstadoUpdate(BaseModel):
    """Schema para cambiar estado de propiedad"""
    estado: str = Field(..., pattern="^(borrador|publicado|pausado|cerrado)$")

class PropiedadResponse(BaseModel):
    """Schema de respuesta de Propiedad"""
    registro_cab_id: int
    titulo: str
    tipo_inmueble: str
    tipo_inmueble_id: int  # ✅ ID del tipo de inmueble (para filtros)
    distrito: str
    direccion: str
    latitud: Optional[Decimal]  # 🗺️ Para mapa
    longitud: Optional[Decimal]  # 🗺️ Para mapa
    telefono: Optional[str] = ""  # Puede ser vacío
    email: Optional[str] = ""  # Puede ser vacío
    propietario_nombre: Optional[str] = ""  # Nombre del propietario
    transaccion: str
    precio_alquiler: Optional[Decimal]
    precio_venta: Optional[Decimal]
    moneda: str
    area: Decimal
    habitaciones: Optional[int] = None
    banos: Optional[int] = None
    estacionamientos: Optional[int] = None
    implementacion: Optional[int] = None
    imagen_principal: Optional[str]
    imagenes: Optional[List[str]] = []  # 🔥 AGREGADO para carrusel
    estado: str
    estado_crm: str
    vistas: int
    contactos: int
    created_at: datetime
    es_favorito: bool = False  # Si el usuario autenticado la tiene en favoritos

    class Config:
        from_attributes = True

class Propietario(BaseModel):
    """Schema para propietario"""
    nombre: str
    telefono: str
    email: Optional[str] = None
    dni: Optional[str] = None  # Solo para dueño/admin

class Corredor(BaseModel):
    """Schema para corredor"""
    usuario_id: Optional[int] = None
    nombre: str
    telefono: str
    email: str

class PropiedadDetalleResponse(PropiedadResponse):
    """Schema de respuesta detallada de Propiedad"""
    nombre_inmueble: Optional[str]  # Nombre del inmueble
    descripcion: Optional[str]
    direccion: str
    latitud: Optional[Decimal]
    longitud: Optional[Decimal]
    antiguedad: Optional[int]
    imagenes: Optional[List[str]]
    propietario: dict  # Mantener dict para flexibilidad
    corredor: Optional[dict]
    caracteristicas: List[dict]
    estado_crm: str
    compartidos: int
    padre_registro_cab_id: Optional[int] = None  # ID del edificio padre (para oficinas)
    piso: Optional[int] = None  # Número de piso (para oficinas/departamentos)

    class Config:
        from_attributes = True

class PropiedadListResponse(BaseModel):
    """Schema para lista de propiedades"""
    propiedades: List[PropiedadResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class EdificioRapidoCreate(BaseModel):
    """Schema para crear edificio rapido desde formulario de oficina"""
    nombre_inmueble: str = Field(..., min_length=5, max_length=200)
    direccion: str = Field(..., min_length=10, max_length=300)
    distrito_id: int
    propietario_id: int
