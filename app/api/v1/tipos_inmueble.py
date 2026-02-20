"""
🏠 API de Tipos de Inmueble
Sistema Inmobiliario - CRUD completo
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func
from typing import List, Optional
from app.database import get_db
from app.dependencies import require_admin, get_optional_user
from app.models.tipo_inmueble import TipoInmueble
from app.models.caracteristica_x_inmueble import CaracteristicaXInmueble
from app.models.usuario import Usuario
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class TipoInmuebleBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    icono: Optional[str] = Field(None, max_length=50)
    orden: int = 0
    activo: bool = True

class TipoInmuebleCreate(TipoInmuebleBase):
    pass

class TipoInmuebleUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    icono: Optional[str] = Field(None, max_length=50)
    orden: Optional[int] = None
    activo: Optional[bool] = None

class TipoInmuebleResponse(TipoInmuebleBase):
    tipo_inmueble_id: int
    total_caracteristicas: Optional[int] = 0

    class Config:
        from_attributes = True


class TipoInmueblePaginado(BaseModel):
    """Respuesta paginada de tipos de inmueble"""
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[TipoInmuebleResponse]


# ============================================
# 📌 ENDPOINTS
# ============================================

@router.get("/", response_model=List[TipoInmuebleResponse])
async def listar_tipos_inmueble(
    activo: Optional[bool] = Query(True, description="Filtrar por estado activo (default: solo activos)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)
):
    """
    📋 Listar todos los tipos de inmueble (por defecto solo activos)
    """
    try:
        query = db.query(TipoInmueble)

        if activo is not None:
            query = query.filter(TipoInmueble.activo == activo)

        tipos = query.order_by(TipoInmueble.orden, TipoInmueble.nombre).all()

        # Obtener conteos de características asignadas por tipo
        conteos = dict(
            db.query(
                CaracteristicaXInmueble.tipo_inmueble_id,
                sa_func.count(CaracteristicaXInmueble.id)
            ).group_by(CaracteristicaXInmueble.tipo_inmueble_id).all()
        )

        # Enriquecer respuesta con total_caracteristicas
        resultado = []
        for tipo in tipos:
            tipo_dict = {
                "tipo_inmueble_id": tipo.tipo_inmueble_id,
                "nombre": tipo.nombre,
                "descripcion": tipo.descripcion,
                "icono": tipo.icono,
                "orden": tipo.orden,
                "activo": tipo.activo,
                "total_caracteristicas": conteos.get(tipo.tipo_inmueble_id, 0)
            }
            resultado.append(tipo_dict)

        return resultado

    except Exception as e:
        logger.error(f"Error listando tipos de inmueble: {e}")
        raise HTTPException(status_code=500, detail="Error al listar tipos de inmueble")

@router.get("/paginado", response_model=TipoInmueblePaginado)
async def listar_tipos_inmueble_paginado(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=100),
    activo: Optional[bool] = Query(True, description="Filtrar por estado activo (default: solo activos)"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)
):
    """Listar tipos de inmueble con paginación"""
    try:
        query = db.query(TipoInmueble)
        if activo is not None:
            query = query.filter(TipoInmueble.activo == activo)
        if search:
            query = query.filter(TipoInmueble.nombre.ilike(f"%{search}%"))
        total = query.count()
        offset = (page - 1) * page_size
        tipos = query.order_by(TipoInmueble.orden, TipoInmueble.nombre).offset(offset).limit(page_size).all()
        total_pages = (total + page_size - 1) // page_size
        return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "data": tipos}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error al listar tipos")



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
        logger.error(f"Error obteniendo tipo de inmueble {tipo_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener tipo de inmueble")

@router.post("/", response_model=TipoInmuebleResponse, status_code=201)
async def crear_tipo_inmueble(
    tipo_data: TipoInmuebleCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    ➕ Crear un nuevo tipo de inmueble
    """
    try:
        # Verificar si ya existe
        tipo_existente = db.query(TipoInmueble).filter(sa_func.lower(TipoInmueble.nombre) == sa_func.lower(tipo_data.nombre)).first()
        if tipo_existente:
            raise HTTPException(status_code=400, detail="Ya existe un tipo de inmueble con ese nombre")
        
        nuevo_tipo = TipoInmueble(**tipo_data.model_dump())
        db.add(nuevo_tipo)
        db.commit()
        db.refresh(nuevo_tipo)
        
        logger.info(f"Tipo de inmueble creado: {nuevo_tipo.nombre} (ID: {nuevo_tipo.tipo_inmueble_id})")
        
        return nuevo_tipo
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando tipo de inmueble: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear tipo de inmueble: {str(e)}")

@router.put("/{tipo_id}", response_model=TipoInmuebleResponse)
async def actualizar_tipo_inmueble(
    tipo_id: int,
    tipo_data: TipoInmuebleUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
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
        
        logger.info(f"Tipo de inmueble actualizado: {tipo.nombre} (ID: {tipo.tipo_inmueble_id})")
        
        return tipo
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error actualizando tipo de inmueble {tipo_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar tipo de inmueble: {str(e)}")

@router.delete("/{tipo_id}")
async def eliminar_tipo_inmueble(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
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
        
        logger.info(f"Tipo de inmueble desactivado: {tipo.nombre} (ID: {tipo.tipo_inmueble_id})")
        
        return {
            "success": True,
            "message": f"Tipo de inmueble '{tipo.nombre}' desactivado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error eliminando tipo de inmueble {tipo_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar tipo de inmueble: {str(e)}")
