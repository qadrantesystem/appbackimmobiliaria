"""
💳 API de Planes de Suscripción
Sistema Inmobiliario - CRUD de Planes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.plan import Plan
from pydantic import BaseModel, Field
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class PlanBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    precio_mensual: Optional[Decimal] = None
    precio_anual: Optional[Decimal] = None
    moneda: str = Field(default='USD', max_length=3)
    max_propiedades: Optional[int] = None
    max_imagenes_por_propiedad: Optional[int] = None
    destacar_propiedades: bool = False
    soporte_prioritario: bool = False
    caracteristicas: Optional[dict] = None
    activo: bool = True
    orden: int = 0

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    precio_mensual: Optional[Decimal] = None
    precio_anual: Optional[Decimal] = None
    moneda: Optional[str] = Field(None, max_length=3)
    max_propiedades: Optional[int] = None
    max_imagenes_por_propiedad: Optional[int] = None
    destacar_propiedades: Optional[bool] = None
    soporte_prioritario: Optional[bool] = None
    caracteristicas: Optional[dict] = None
    activo: Optional[bool] = None
    orden: Optional[int] = None

class PlanResponse(PlanBase):
    plan_id: int
    
    class Config:
        from_attributes = True

# ============================================
# 📌 ENDPOINTS
# ============================================

@router.get("/", response_model=List[PlanResponse])
async def listar_planes(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db)
):
    """
    📋 Listar todos los planes
    
    - **activo**: Filtrar por planes activos/inactivos (opcional)
    - Ordenados por campo 'orden'
    """
    try:
        query = db.query(Plan)
        
        if activo is not None:
            query = query.filter(Plan.activo == activo)
        
        planes = query.order_by(Plan.orden).all()
        
        return planes
        
    except Exception as e:
        logger.error(f"❌ Error listando planes: {e}")
        raise HTTPException(status_code=500, detail="Error al listar planes")

@router.get("/{plan_id}", response_model=PlanResponse)
async def obtener_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """
    🔍 Obtener un plan por ID
    """
    try:
        plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener plan")

@router.post("/", response_model=PlanResponse, status_code=201)
async def crear_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db)
):
    """
    ➕ Crear un nuevo plan
    """
    try:
        # Verificar si ya existe un plan con ese nombre
        plan_existente = db.query(Plan).filter(Plan.nombre == plan_data.nombre).first()
        if plan_existente:
            raise HTTPException(status_code=400, detail="Ya existe un plan con ese nombre")
        
        # Crear nuevo plan
        nuevo_plan = Plan(**plan_data.model_dump())
        db.add(nuevo_plan)
        db.commit()
        db.refresh(nuevo_plan)
        
        logger.info(f"✅ Plan creado: {nuevo_plan.nombre} (ID: {nuevo_plan.plan_id})")
        
        return nuevo_plan
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creando plan: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear plan: {str(e)}")

@router.put("/{plan_id}", response_model=PlanResponse)
async def actualizar_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    db: Session = Depends(get_db)
):
    """
    ✏️ Actualizar un plan existente
    """
    try:
        plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        
        # Actualizar solo los campos proporcionados
        update_data = plan_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(plan, field, value)
        
        db.commit()
        db.refresh(plan)
        
        logger.info(f"✅ Plan actualizado: {plan.nombre} (ID: {plan.plan_id})")
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar plan: {str(e)}")

@router.delete("/{plan_id}")
async def eliminar_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """
    🗑️ Eliminar un plan (soft delete - marca como inactivo)
    """
    try:
        plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        
        # Soft delete: marcar como inactivo
        plan.activo = False
        db.commit()
        
        logger.info(f"✅ Plan desactivado: {plan.nombre} (ID: {plan.plan_id})")
        
        return {
            "success": True,
            "message": f"Plan '{plan.nombre}' desactivado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error eliminando plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar plan: {str(e)}")

@router.patch("/{plan_id}/activar")
async def activar_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """
    ✅ Activar un plan desactivado
    """
    try:
        plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        
        plan.activo = True
        db.commit()
        
        logger.info(f"✅ Plan activado: {plan.nombre} (ID: {plan.plan_id})")
        
        return {
            "success": True,
            "message": f"Plan '{plan.nombre}' activado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error activando plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al activar plan: {str(e)}")
