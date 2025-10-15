"""
📊 API de Estados CRM
Sistema Inmobiliario - CRUD completo
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.estado_crm import EstadoCRM
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class EstadoCRMBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    color: Optional[str] = Field(None, max_length=20)
    icono: Optional[str] = Field(None, max_length=50)
    orden: int = 0
    es_final: bool = False
    es_ganado: bool = False
    activo: bool = True

class EstadoCRMCreate(EstadoCRMBase):
    pass

class EstadoCRMUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    color: Optional[str] = Field(None, max_length=20)
    icono: Optional[str] = Field(None, max_length=50)
    orden: Optional[int] = None
    es_final: Optional[bool] = None
    es_ganado: Optional[bool] = None
    activo: Optional[bool] = None

class EstadoCRMResponse(EstadoCRMBase):
    estado_id: int
    
    class Config:
        from_attributes = True

# ============================================
# 📌 ENDPOINTS
# ============================================

@router.get("/", response_model=List[EstadoCRMResponse])
async def listar_estados_crm(
    activo: Optional[bool] = Query(None),
    es_final: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """📋 Listar todos los estados CRM"""
    try:
        query = db.query(EstadoCRM)
        
        if activo is not None:
            query = query.filter(EstadoCRM.activo == activo)
        
        if es_final is not None:
            query = query.filter(EstadoCRM.es_final == es_final)
        
        estados = query.order_by(EstadoCRM.orden, EstadoCRM.nombre).all()
        
        return estados
        
    except Exception as e:
        logger.error(f"❌ Error listando estados CRM: {e}")
        raise HTTPException(status_code=500, detail="Error al listar estados CRM")

@router.get("/{estado_id}", response_model=EstadoCRMResponse)
async def obtener_estado_crm(
    estado_id: int,
    db: Session = Depends(get_db)
):
    """🔍 Obtener un estado CRM por ID"""
    try:
        estado = db.query(EstadoCRM).filter(EstadoCRM.estado_id == estado_id).first()
        
        if not estado:
            raise HTTPException(status_code=404, detail="Estado CRM no encontrado")
        
        return estado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado CRM {estado_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener estado CRM")

@router.post("/", response_model=EstadoCRMResponse, status_code=201)
async def crear_estado_crm(
    estado_data: EstadoCRMCreate,
    db: Session = Depends(get_db)
):
    """➕ Crear un nuevo estado CRM"""
    try:
        # Verificar si ya existe el código
        existe = db.query(EstadoCRM).filter(EstadoCRM.codigo == estado_data.codigo).first()
        if existe:
            raise HTTPException(status_code=400, detail="Ya existe un estado con ese código")
        
        nuevo_estado = EstadoCRM(**estado_data.model_dump())
        db.add(nuevo_estado)
        db.commit()
        db.refresh(nuevo_estado)
        
        logger.info(f"✅ Estado CRM creado: {nuevo_estado.nombre} (ID: {nuevo_estado.estado_id})")
        
        return nuevo_estado
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creando estado CRM: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear estado CRM: {str(e)}")

@router.put("/{estado_id}", response_model=EstadoCRMResponse)
async def actualizar_estado_crm(
    estado_id: int,
    estado_data: EstadoCRMUpdate,
    db: Session = Depends(get_db)
):
    """✏️ Actualizar un estado CRM"""
    try:
        estado = db.query(EstadoCRM).filter(EstadoCRM.estado_id == estado_id).first()
        
        if not estado:
            raise HTTPException(status_code=404, detail="Estado CRM no encontrado")
        
        update_data = estado_data.model_dump(exclude_unset=True)
        
        # Si se actualiza el código, verificar que no exista
        if 'codigo' in update_data:
            existe = db.query(EstadoCRM).filter(
                EstadoCRM.codigo == update_data['codigo'],
                EstadoCRM.estado_id != estado_id
            ).first()
            if existe:
                raise HTTPException(status_code=400, detail="Ya existe un estado con ese código")
        
        for field, value in update_data.items():
            setattr(estado, field, value)
        
        db.commit()
        db.refresh(estado)
        
        logger.info(f"✅ Estado CRM actualizado: {estado.nombre} (ID: {estado.estado_id})")
        
        return estado
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando estado CRM {estado_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar estado CRM: {str(e)}")

@router.delete("/{estado_id}")
async def eliminar_estado_crm(
    estado_id: int,
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar un estado CRM (soft delete)"""
    try:
        estado = db.query(EstadoCRM).filter(EstadoCRM.estado_id == estado_id).first()
        
        if not estado:
            raise HTTPException(status_code=404, detail="Estado CRM no encontrado")
        
        estado.activo = False
        db.commit()
        
        logger.info(f"✅ Estado CRM desactivado: {estado.nombre} (ID: {estado.estado_id})")
        
        return {
            "success": True,
            "message": f"Estado CRM '{estado.nombre}' desactivado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error eliminando estado CRM {estado_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar estado CRM: {str(e)}")
