"""
🔗 API de Características por Tipo de Inmueble
Sistema Inmobiliario - CRUD completo
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.caracteristica_x_inmueble import CaracteristicaXInmueble
from app.models.caracteristica import Caracteristica
from app.models.tipo_inmueble import TipoInmueble
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class CaracteristicaXInmuebleBase(BaseModel):
    tipo_inmueble_id: int
    caracteristica_id: int
    requerido: bool = False
    visible_en_filtro: bool = True
    orden: int = 0

class CaracteristicaXInmuebleCreate(CaracteristicaXInmuebleBase):
    pass

class CaracteristicaXInmuebleUpdate(BaseModel):
    requerido: Optional[bool] = None
    visible_en_filtro: Optional[bool] = None
    orden: Optional[int] = None

class CaracteristicaXInmuebleResponse(CaracteristicaXInmuebleBase):
    id: int
    
    class Config:
        from_attributes = True

class CaracteristicaDetalle(BaseModel):
    caracteristica_id: int
    nombre: str
    descripcion: Optional[str]
    tipo_input: Optional[str]
    unidad: Optional[str]
    categoria: Optional[str]
    requerido: bool
    visible_en_filtro: bool
    orden: int
    
    class Config:
        from_attributes = True

# ============================================
# 📌 ENDPOINTS
# ============================================

@router.get("/tipo-inmueble/{tipo_inmueble_id}", response_model=List[CaracteristicaDetalle])
async def listar_caracteristicas_por_tipo(
    tipo_inmueble_id: int,
    db: Session = Depends(get_db)
):
    """
    📋 Listar características de un tipo de inmueble específico
    Retorna las características con sus detalles
    """
    try:
        # Verificar que el tipo de inmueble existe
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == tipo_inmueble_id).first()
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de inmueble no encontrado")
        
        # Obtener características asociadas
        relaciones = db.query(
            CaracteristicaXInmueble, Caracteristica
        ).join(
            Caracteristica, CaracteristicaXInmueble.caracteristica_id == Caracteristica.caracteristica_id
        ).filter(
            CaracteristicaXInmueble.tipo_inmueble_id == tipo_inmueble_id
        ).order_by(
            CaracteristicaXInmueble.orden, Caracteristica.nombre
        ).all()
        
        resultado = []
        for rel, car in relaciones:
            resultado.append({
                "caracteristica_id": car.caracteristica_id,
                "nombre": car.nombre,
                "descripcion": car.descripcion,
                "tipo_input": car.tipo_input,
                "unidad": car.unidad,
                "categoria": car.categoria,
                "requerido": rel.requerido,
                "visible_en_filtro": rel.visible_en_filtro,
                "orden": rel.orden
            })
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error listando características del tipo {tipo_inmueble_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al listar características")

@router.post("/", response_model=CaracteristicaXInmuebleResponse, status_code=201)
async def asignar_caracteristica_a_tipo(
    data: CaracteristicaXInmuebleCreate,
    db: Session = Depends(get_db)
):
    """➕ Asignar una característica a un tipo de inmueble"""
    try:
        # Verificar que existen
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == data.tipo_inmueble_id).first()
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de inmueble no encontrado")
        
        caracteristica = db.query(Caracteristica).filter(Caracteristica.caracteristica_id == data.caracteristica_id).first()
        if not caracteristica:
            raise HTTPException(status_code=404, detail="Característica no encontrada")
        
        # Verificar si ya existe la relación
        existe = db.query(CaracteristicaXInmueble).filter(
            CaracteristicaXInmueble.tipo_inmueble_id == data.tipo_inmueble_id,
            CaracteristicaXInmueble.caracteristica_id == data.caracteristica_id
        ).first()
        
        if existe:
            raise HTTPException(status_code=400, detail="Esta característica ya está asignada a este tipo de inmueble")
        
        nueva_relacion = CaracteristicaXInmueble(**data.model_dump())
        db.add(nueva_relacion)
        db.commit()
        db.refresh(nueva_relacion)
        
        logger.info(f"✅ Característica {data.caracteristica_id} asignada al tipo {data.tipo_inmueble_id}")
        
        return nueva_relacion
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error asignando característica: {e}")
        raise HTTPException(status_code=500, detail=f"Error al asignar característica: {str(e)}")

@router.put("/{relacion_id}", response_model=CaracteristicaXInmuebleResponse)
async def actualizar_caracteristica_tipo(
    relacion_id: int,
    data: CaracteristicaXInmuebleUpdate,
    db: Session = Depends(get_db)
):
    """✏️ Actualizar configuración de característica en tipo de inmueble"""
    try:
        relacion = db.query(CaracteristicaXInmueble).filter(CaracteristicaXInmueble.id == relacion_id).first()
        
        if not relacion:
            raise HTTPException(status_code=404, detail="Relación no encontrada")
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(relacion, field, value)
        
        db.commit()
        db.refresh(relacion)
        
        logger.info(f"✅ Relación actualizada (ID: {relacion_id})")
        
        return relacion
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando relación {relacion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")

@router.delete("/{relacion_id}")
async def eliminar_caracteristica_tipo(
    relacion_id: int,
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar asignación de característica a tipo de inmueble"""
    try:
        relacion = db.query(CaracteristicaXInmueble).filter(CaracteristicaXInmueble.id == relacion_id).first()
        
        if not relacion:
            raise HTTPException(status_code=404, detail="Relación no encontrada")
        
        db.delete(relacion)
        db.commit()
        
        logger.info(f"✅ Relación eliminada (ID: {relacion_id})")
        
        return {
            "success": True,
            "message": "Característica desasignada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error eliminando relación {relacion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")
