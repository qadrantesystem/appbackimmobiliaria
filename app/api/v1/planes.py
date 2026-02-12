"""
💳 API de Planes de Suscripción
Sistema Inmobiliario - CRUD de Planes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func
from app.database import get_db
from app.dependencies import get_current_user, require_admin, get_optional_user
from app.models.plan import Plan
from app.models.usuario import Usuario
from pydantic import BaseModel, Field
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class PlanBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio_mensual: Optional[Decimal] = Field(None, ge=0)
    precio_anual: Optional[Decimal] = Field(None, ge=0)
    moneda: str = Field(default='USD', max_length=3)
    max_propiedades: Optional[int] = Field(None, ge=0, le=10000)
    max_imagenes_por_propiedad: Optional[int] = Field(None, ge=0, le=100)
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


class PlanPaginado(BaseModel):
    """Respuesta paginada de planes"""
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[PlanResponse]


# ============================================
# 📌 ENDPOINTS
# ============================================

@router.get("/", response_model=List[PlanResponse])
async def listar_planes(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)  # Público pero puede personalizar
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
        logger.error(f"Error listando planes: {e}")
        raise HTTPException(status_code=500, detail="Error al listar planes")

@router.get("/paginado", response_model=PlanPaginado)
async def listar_planes_paginado(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=100),
    activo: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)
):
    """Listar planes con paginación"""
    try:
        query = db.query(Plan)
        if activo is not None:
            query = query.filter(Plan.activo == activo)
        if search:
            query = query.filter(Plan.nombre.ilike(f"%{search}%"))
        total = query.count()
        offset = (page - 1) * page_size
        planes = query.order_by(Plan.orden, Plan.nombre).offset(offset).limit(page_size).all()
        total_pages = (total + page_size - 1) // page_size
        return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "data": planes}
    except Exception as e:
        logger.error(f"Error: {e}")
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
        logger.error(f"Error obteniendo plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener plan")

@router.post("/", response_model=PlanResponse, status_code=201)
async def crear_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)  # Solo ADMIN
):
    """
    ➕ Crear un nuevo plan
    """
    try:
        # Verificar si ya existe un plan con ese nombre
        plan_existente = db.query(Plan).filter(func.lower(Plan.nombre) == func.lower(plan_data.nombre)).first()
        if plan_existente:
            raise HTTPException(status_code=400, detail="Ya existe un plan con ese nombre")
        
        # Crear nuevo plan
        nuevo_plan = Plan(**plan_data.model_dump())
        db.add(nuevo_plan)
        db.commit()
        db.refresh(nuevo_plan)
        
        logger.info(f"Plan creado: {nuevo_plan.nombre} (ID: {nuevo_plan.plan_id})")
        
        return nuevo_plan
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando plan: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear plan: {str(e)}")

@router.put("/{plan_id}", response_model=PlanResponse)
async def actualizar_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)  # Solo ADMIN
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
        
        logger.info(f"Plan actualizado: {plan.nombre} (ID: {plan.plan_id})")
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error actualizando plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar plan: {str(e)}")

@router.delete("/{plan_id}")
async def eliminar_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)  # Solo ADMIN
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
        
        logger.info(f"Plan desactivado: {plan.nombre} (ID: {plan.plan_id})")
        
        return {
            "success": True,
            "message": f"Plan '{plan.nombre}' desactivado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error eliminando plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar plan: {str(e)}")

@router.patch("/{plan_id}/activar")
async def activar_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)  # Solo ADMIN
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
        
        logger.info(f"Plan activado: {plan.nombre} (ID: {plan.plan_id})")
        
        return {
            "success": True,
            "message": f"Plan '{plan.nombre}' activado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error activando plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al activar plan: {str(e)}")
