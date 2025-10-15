"""
🏠 API de Tipos de Inmueble
Sistema Inmobiliario - CRUD completo
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.tipo_inmueble import TipoInmueble
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class TipoInmuebleBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    icono: Optional[str] = Field(None, max_length=50)
    orden: int = 0
    activo: bool = True

class TipoInmuebleCreate(TipoInmuebleBase):
    pass

class TipoInmuebleUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    icono: Optional[str] = Field(None, max_length=50)
    orden: Optional[int] = None
    activo: Optional[bool] = None

class TipoInmuebleResponse(TipoInmuebleBase):
    tipo_inmueble_id: int
    
    class Config:
        from_attributes = True

# ============================================
# 📌 ENDPOINTS
# ============================================

@router.get("/", response_model=List[TipoInmuebleResponse])
async def listar_tipos_inmueble(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db)
):
    """
    📋 Listar todos los tipos de inmueble
    """
    try:
        query = db.query(TipoInmueble)
        
        if activo is not None:
            query = query.filter(TipoInmueble.activo == activo)
        
        tipos = query.order_by(TipoInmueble.orden, TipoInmueble.nombre).all()
        
        return tipos
        
    except Exception as e:
        logger.error(f"❌ Error listando tipos de inmueble: {e}")
        raise HTTPException(status_code=500, detail="Error al listar tipos de inmueble")

@router.get("/{tipo_id}", response_model=TipoInmuebleResponse)
async def obtener_tipo_inmueble(
    tipo_id: int,
    db: Session = Depends(get_db)
):
    """
    🔍 Obtener un tipo de inmueble por ID
    """
    try:
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == tipo_id).first()
        
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de inmueble no encontrado")
        
        return tipo
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo tipo de inmueble {tipo_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener tipo de inmueble")

@router.post("/", response_model=TipoInmuebleResponse, status_code=201)
async def crear_tipo_inmueble(
    tipo_data: TipoInmuebleCreate,
    db: Session = Depends(get_db)
):
    """
    ➕ Crear un nuevo tipo de inmueble
    """
    try:
        # Verificar si ya existe
        tipo_existente = db.query(TipoInmueble).filter(TipoInmueble.nombre == tipo_data.nombre).first()
        if tipo_existente:
            raise HTTPException(status_code=400, detail="Ya existe un tipo de inmueble con ese nombre")
        
        nuevo_tipo = TipoInmueble(**tipo_data.model_dump())
        db.add(nuevo_tipo)
        db.commit()
        db.refresh(nuevo_tipo)
        
        logger.info(f"✅ Tipo de inmueble creado: {nuevo_tipo.nombre} (ID: {nuevo_tipo.tipo_inmueble_id})")
        
        return nuevo_tipo
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creando tipo de inmueble: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear tipo de inmueble: {str(e)}")

@router.put("/{tipo_id}", response_model=TipoInmuebleResponse)
async def actualizar_tipo_inmueble(
    tipo_id: int,
    tipo_data: TipoInmuebleUpdate,
    db: Session = Depends(get_db)
):
    """
    ✏️ Actualizar un tipo de inmueble
    """
    try:
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == tipo_id).first()
        
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de inmueble no encontrado")
        
        update_data = tipo_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(tipo, field, value)
        
        db.commit()
        db.refresh(tipo)
        
        logger.info(f"✅ Tipo de inmueble actualizado: {tipo.nombre} (ID: {tipo.tipo_inmueble_id})")
        
        return tipo
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando tipo de inmueble {tipo_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar tipo de inmueble: {str(e)}")

@router.delete("/{tipo_id}")
async def eliminar_tipo_inmueble(
    tipo_id: int,
    db: Session = Depends(get_db)
):
    """
    🗑️ Eliminar un tipo de inmueble (soft delete)
    """
    try:
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == tipo_id).first()
        
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de inmueble no encontrado")
        
        tipo.activo = False
        db.commit()
        
        logger.info(f"✅ Tipo de inmueble desactivado: {tipo.nombre} (ID: {tipo.tipo_inmueble_id})")
        
        return {
            "success": True,
            "message": f"Tipo de inmueble '{tipo.nombre}' desactivado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error eliminando tipo de inmueble {tipo_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar tipo de inmueble: {str(e)}")
