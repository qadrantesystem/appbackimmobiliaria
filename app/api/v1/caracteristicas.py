"""
⭐ API de Características
Sistema Inmobiliario - CRUD completo
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.dependencies import require_admin, get_optional_user
from app.models.caracteristica import Caracteristica
from app.models.usuario import Usuario
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class CaracteristicaBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    tipo_input: Optional[str] = Field(None, max_length=50)
    unidad: Optional[str] = Field(None, max_length=20)
    categoria: Optional[str] = Field(None, max_length=50)
    orden: int = 0
    activo: bool = True

class CaracteristicaCreate(CaracteristicaBase):
    pass

class CaracteristicaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    tipo_input: Optional[str] = Field(None, max_length=50)
    unidad: Optional[str] = Field(None, max_length=20)
    categoria: Optional[str] = Field(None, max_length=50)
    orden: Optional[int] = None
    activo: Optional[bool] = None

class CaracteristicaResponse(CaracteristicaBase):
    caracteristica_id: int
    
    class Config:
        from_attributes = True


class CaracteristicaPaginada(BaseModel):
    """Respuesta paginada de características"""
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[CaracteristicaResponse]


# ============================================
# 📌 ENDPOINTS
# ============================================

@router.get("/", response_model=List[CaracteristicaResponse])
async def listar_caracteristicas(
    activo: Optional[bool] = Query(None),
    categoria: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)
):
    """📋 Listar todas las características"""
    try:
        query = db.query(Caracteristica)
        
        if activo is not None:
            query = query.filter(Caracteristica.activo == activo)
        
        if categoria:
            query = query.filter(Caracteristica.categoria == categoria)
        
        caracteristicas = query.order_by(Caracteristica.categoria, Caracteristica.orden, Caracteristica.nombre).all()
        
        return caracteristicas
        
    except Exception as e:
        logger.error(f"❌ Error listando características: {e}")
        raise HTTPException(status_code=500, detail="Error al listar características")


@router.get("/paginado", response_model=CaracteristicaPaginada)
async def listar_caracteristicas_paginado(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(5, ge=1, le=100, description="Tamaño de página"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)
):
    """
    📄 Listar características con paginación (por defecto 5 registros)
    
    - **page**: Número de página (default: 1)
    - **page_size**: Cantidad de registros por página (default: 5, max: 100)
    - **activo**: Filtrar por estado activo/inactivo (opcional)
    - **search**: Buscar por nombre (opcional)
    """
    try:
        # Query base
        query = db.query(Caracteristica)
        
        # Filtros
        if activo is not None:
            query = query.filter(Caracteristica.activo == activo)
        
        if search:
            query = query.filter(Caracteristica.nombre.ilike(f"%{search}%"))
        
        # Total de registros
        total = query.count()
        
        # Paginación
        offset = (page - 1) * page_size
        caracteristicas = query.order_by(
            Caracteristica.categoria, 
            Caracteristica.orden, 
            Caracteristica.nombre
        ).offset(offset).limit(page_size).all()
        
        # Calcular total de páginas
        total_pages = (total + page_size - 1) // page_size
        
        logger.info(f"✅ Listadas {len(caracteristicas)} características (página {page}/{total_pages})")
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "data": caracteristicas
        }
        
    except Exception as e:
        logger.error(f"❌ Error listando características paginadas: {e}")
        raise HTTPException(status_code=500, detail="Error al listar características")


@router.get("/{caracteristica_id}", response_model=CaracteristicaResponse)
async def obtener_caracteristica(
    caracteristica_id: int,
    db: Session = Depends(get_db)
):
    """🔍 Obtener una característica por ID"""
    try:
        caracteristica = db.query(Caracteristica).filter(Caracteristica.caracteristica_id == caracteristica_id).first()
        
        if not caracteristica:
            raise HTTPException(status_code=404, detail="Característica no encontrada")
        
        return caracteristica
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo característica {caracteristica_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener característica")

@router.post("/", response_model=CaracteristicaResponse, status_code=201)
async def crear_caracteristica(
    caracteristica_data: CaracteristicaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """➕ Crear una nueva característica"""
    try:
        nueva_caracteristica = Caracteristica(**caracteristica_data.model_dump())
        db.add(nueva_caracteristica)
        db.commit()
        db.refresh(nueva_caracteristica)
        
        logger.info(f"✅ Característica creada: {nueva_caracteristica.nombre} (ID: {nueva_caracteristica.caracteristica_id})")
        
        return nueva_caracteristica
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creando característica: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear característica: {str(e)}")

@router.put("/{caracteristica_id}", response_model=CaracteristicaResponse)
async def actualizar_caracteristica(
    caracteristica_id: int,
    caracteristica_data: CaracteristicaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """✏️ Actualizar una característica"""
    try:
        caracteristica = db.query(Caracteristica).filter(Caracteristica.caracteristica_id == caracteristica_id).first()
        
        if not caracteristica:
            raise HTTPException(status_code=404, detail="Característica no encontrada")
        
        update_data = caracteristica_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(caracteristica, field, value)
        
        db.commit()
        db.refresh(caracteristica)
        
        logger.info(f"✅ Característica actualizada: {caracteristica.nombre} (ID: {caracteristica.caracteristica_id})")
        
        return caracteristica
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando característica {caracteristica_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar característica: {str(e)}")

@router.delete("/{caracteristica_id}")
async def eliminar_caracteristica(
    caracteristica_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """🗑️ Eliminar una característica (soft delete)"""
    try:
        caracteristica = db.query(Caracteristica).filter(Caracteristica.caracteristica_id == caracteristica_id).first()
        
        if not caracteristica:
            raise HTTPException(status_code=404, detail="Característica no encontrada")
        
        caracteristica.activo = False
        db.commit()
        
        logger.info(f"✅ Característica desactivada: {caracteristica.nombre} (ID: {caracteristica.caracteristica_id})")
        
        return {
            "success": True,
            "message": f"Característica '{caracteristica.nombre}' desactivada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error eliminando característica {caracteristica_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar característica: {str(e)}")
