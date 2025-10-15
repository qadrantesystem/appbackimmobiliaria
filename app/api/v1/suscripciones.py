"""
💳 API de Suscripciones
Sistema Inmobiliario - Gestión de suscripciones de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.suscripcion import Suscripcion
from app.models.plan import Plan
from app.models.usuario import Usuario
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class SuscripcionBase(BaseModel):
    plan_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
    monto_pagado: Decimal
    metodo_pago: Optional[str] = None
    transaccion_id: Optional[str] = None
    auto_renovar: bool = True

class SuscripcionCreate(SuscripcionBase):
    usuario_id: Optional[int] = None  # Admin puede especificar, usuario usa su propio ID

class SuscripcionUpdate(BaseModel):
    auto_renovar: Optional[bool] = None
    estado: Optional[str] = Field(None, pattern="^(activa|cancelada|expirada|suspendida)$")

class SuscripcionResponse(SuscripcionBase):
    suscripcion_id: int
    usuario_id: int
    estado: str
    created_at: datetime
    cancelada_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SuscripcionDetalle(SuscripcionResponse):
    plan_nombre: str
    plan_descripcion: Optional[str]
    usuario_email: str
    usuario_nombre: str

# ============================================
# 📌 ENDPOINTS
# ============================================

@router.get("/", response_model=List[SuscripcionDetalle])
async def listar_suscripciones(
    estado: Optional[str] = Query(None, pattern="^(activa|cancelada|expirada|suspendida)$"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    📋 Listar suscripciones
    - Usuario normal: solo ve sus propias suscripciones
    - Admin: ve todas las suscripciones
    """
    try:
        query = db.query(Suscripcion, Plan, Usuario).join(
            Plan, Suscripcion.plan_id == Plan.plan_id
        ).join(
            Usuario, Suscripcion.usuario_id == Usuario.usuario_id
        )
        
        # Si no es admin, solo ve sus suscripciones
        if current_user.perfil_id != 4:  # 4 = admin
            query = query.filter(Suscripcion.usuario_id == current_user.usuario_id)
        
        if estado:
            query = query.filter(Suscripcion.estado == estado)
        
        resultados = query.order_by(Suscripcion.created_at.desc()).all()
        
        suscripciones = []
        for susc, plan, usuario in resultados:
            suscripciones.append({
                **susc.__dict__,
                "plan_nombre": plan.nombre,
                "plan_descripcion": plan.descripcion,
                "usuario_email": usuario.email,
                "usuario_nombre": f"{usuario.nombre} {usuario.apellido}"
            })
        
        return suscripciones
        
    except Exception as e:
        logger.error(f"❌ Error listando suscripciones: {e}")
        raise HTTPException(status_code=500, detail="Error al listar suscripciones")

@router.get("/me", response_model=List[SuscripcionDetalle])
async def mis_suscripciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """📋 Ver mis suscripciones"""
    try:
        resultados = db.query(Suscripcion, Plan, Usuario).join(
            Plan, Suscripcion.plan_id == Plan.plan_id
        ).join(
            Usuario, Suscripcion.usuario_id == Usuario.usuario_id
        ).filter(
            Suscripcion.usuario_id == current_user.usuario_id
        ).order_by(Suscripcion.created_at.desc()).all()
        
        suscripciones = []
        for susc, plan, usuario in resultados:
            suscripciones.append({
                **susc.__dict__,
                "plan_nombre": plan.nombre,
                "plan_descripcion": plan.descripcion,
                "usuario_email": usuario.email,
                "usuario_nombre": f"{usuario.nombre} {usuario.apellido}"
            })
        
        return suscripciones
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo mis suscripciones: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener suscripciones")

@router.get("/{suscripcion_id}", response_model=SuscripcionDetalle)
async def obtener_suscripcion(
    suscripcion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """🔍 Obtener una suscripción por ID"""
    try:
        resultado = db.query(Suscripcion, Plan, Usuario).join(
            Plan, Suscripcion.plan_id == Plan.plan_id
        ).join(
            Usuario, Suscripcion.usuario_id == Usuario.usuario_id
        ).filter(Suscripcion.suscripcion_id == suscripcion_id).first()
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Suscripción no encontrada")
        
        susc, plan, usuario = resultado
        
        # Verificar permisos
        if current_user.perfil_id != 4 and susc.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para ver esta suscripción")
        
        return {
            **susc.__dict__,
            "plan_nombre": plan.nombre,
            "plan_descripcion": plan.descripcion,
            "usuario_email": usuario.email,
            "usuario_nombre": f"{usuario.nombre} {usuario.apellido}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo suscripción {suscripcion_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener suscripción")

@router.post("/", response_model=SuscripcionResponse, status_code=201)
async def crear_suscripcion(
    suscripcion_data: SuscripcionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """➕ Crear una nueva suscripción"""
    try:
        # Si no es admin, usar el ID del usuario actual
        usuario_id = suscripcion_data.usuario_id if current_user.perfil_id == 4 else current_user.usuario_id
        
        # Verificar que el plan existe
        plan = db.query(Plan).filter(Plan.plan_id == suscripcion_data.plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        
        nueva_suscripcion = Suscripcion(
            usuario_id=usuario_id,
            **suscripcion_data.model_dump(exclude={"usuario_id"})
        )
        
        db.add(nueva_suscripcion)
        db.commit()
        db.refresh(nueva_suscripcion)
        
        logger.info(f"✅ Suscripción creada: usuario={usuario_id}, plan={suscripcion_data.plan_id}")
        
        return nueva_suscripcion
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creando suscripción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear suscripción: {str(e)}")

@router.patch("/{suscripcion_id}/cancelar")
async def cancelar_suscripcion(
    suscripcion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """🚫 Cancelar una suscripción"""
    try:
        suscripcion = db.query(Suscripcion).filter(Suscripcion.suscripcion_id == suscripcion_id).first()
        
        if not suscripcion:
            raise HTTPException(status_code=404, detail="Suscripción no encontrada")
        
        # Verificar permisos
        if current_user.perfil_id != 4 and suscripcion.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para cancelar esta suscripción")
        
        suscripcion.estado = "cancelada"
        suscripcion.cancelada_at = datetime.now()
        suscripcion.auto_renovar = False
        
        db.commit()
        
        logger.info(f"✅ Suscripción cancelada: {suscripcion_id}")
        
        return {
            "success": True,
            "message": "Suscripción cancelada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error cancelando suscripción {suscripcion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al cancelar suscripción: {str(e)}")

@router.put("/{suscripcion_id}", response_model=SuscripcionResponse)
async def actualizar_suscripcion(
    suscripcion_id: int,
    suscripcion_data: SuscripcionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)  # Solo admin
):
    """✏️ Actualizar una suscripción (solo admin)"""
    try:
        suscripcion = db.query(Suscripcion).filter(Suscripcion.suscripcion_id == suscripcion_id).first()
        
        if not suscripcion:
            raise HTTPException(status_code=404, detail="Suscripción no encontrada")
        
        update_data = suscripcion_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(suscripcion, field, value)
        
        db.commit()
        db.refresh(suscripcion)
        
        logger.info(f"✅ Suscripción actualizada: {suscripcion_id}")
        
        return suscripcion
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando suscripción {suscripcion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar suscripción: {str(e)}")
